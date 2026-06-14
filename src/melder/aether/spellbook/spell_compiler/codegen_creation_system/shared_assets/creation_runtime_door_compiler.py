from typing import Optional, Any, Callable, Sequence

from melder.aether.spellbook.spell_compiler.executor_code_cache import (
    get_or_compile_executor_code,
)

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
        - Caller must ensure the override payload is absent for this lane.
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
        Provide the hooks override lane with no local `overrides are None`
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
) -> Callable[..., Callable[..., Any]]:
    """
    Return the no-hooks overrides-only template factory for one resolve route.

    This is the route selector for the override-bearing instance lane. It maps
    the builder-selected existence route onto the precompiled template family
    that emits the correct runtime body for that route.
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
) -> Callable[..., Callable[..., Any]]:
    """
    Return the hook-aware overrides-only template factory for one resolve
    route.

    This is the hook-lane companion to `_select_overrides_only_template`,
    choosing the template family that returns `(instance, created)` for hook
    activation routing.
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
) -> Callable[..., Callable[..., Any]]:
    """
    Return the no-hooks no-overrides template factory for one route/fast-path
    combination.

    The additional `use_fast_transient` bit matters only for transient-many
    spells, where the runtime may bypass the standard creation call shape and
    use a tighter direct executor lane.
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
) -> Callable[..., Callable[..., Any]]:
    """
    Return the hook-aware no-overrides template factory for one route/fast
    combination.

    This is the hook-lane counterpart to
    `_select_no_overrides_only_template`, preserving the same route selection
    semantics while targeting the `(instance, created)` return contract.
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
    Compile the route-specific overrides-only template factory.

    The emitted factory later receives spell-static bindings and returns the
    concrete runtime callable used for one override-bearing creation-context
    lane.
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
    Compile the route-specific no-overrides template factory.

    This is the no-override counterpart to the override template compiler,
    including the optional fast-transient specialization bit for the transient
    many route.
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
) -> Callable[..., Callable[..., Any]]:
    """
    Compile emitted template source and resolve one expected callable export.

    Contract:
        - Executes compiled `source` in an isolated local namespace.
        - Returns the callable named by `expected_callable_name`.
        - Raises RuntimeError with caller-provided messages for compile or export
          contract failures.
    """
    local_namespace: dict[str, Callable[..., Callable[..., Any]]] = {}
    try:
        exec(
            get_or_compile_executor_code(
                source=source,
                source_name=source_name,
            ),
            {},
            local_namespace,
        )
    except Exception as exc:
        raise RuntimeError(compile_error_message) from exc
    template = local_namespace.get(expected_callable_name)
    if template is not None:
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
    Build the synthetic compile filename for one emitted template shape.

    The source name is deterministic, so tracebacks, debugging output, and
    compile caches remain readable and stable across repeated runs for the same
    route/template combination.
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
    Assemble the emitted Python source for one template-factory/executor pair.

    All higher-level source builders eventually funnel through this helper. It
    creates the outer template factory plus the inner runtime-callable body that
    will later be compiled and resolved by name.
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
    Build the full emitted source string for a no-overrides template family.

    This is the thin wrapper that binds the route-specific body lines into the
    shared outer template/executor source shape for no-override lanes.
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
        execution_signature="caller_creations, root_creations=None",
        execution_lines=no_overrides_lines,
    )


def _build_overrides_only_template_source(
        *,
        with_overrides_lines: Sequence[str],
) -> str:
    """
    Build the full emitted source string for an overrides-only template family.

    This is the override-bearing counterpart to
    `_build_no_overrides_only_template_source`, binding route-specific override
    body lines into the shared template/executor source skeleton.
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
        execution_signature="caller_creations, overrides, root_creations=None",
        execution_lines=with_overrides_lines,
    )


def _build_no_overrides_lines(
        *,
        resolve_route_key: str,
        fast_transient_no_overrides_enabled: bool,
        return_created: bool,
) -> Sequence[str]:
    """
    Build the route-specific runtime body for no-override execution.

    The returned lines are the inner emitted executor body for the chosen
    existence route. This is where route semantics such as existing-creation
    reuse, spellspace enforcement, shared-instance reuse, or transient creation
    are converted into emitted Python statements.
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
            "creation = caller_creations.get_creation(_spell_id)",
            "if creation is not None:",
            _prefix_one_indent(
                _build_return_statement(
                    value_expression="creation",
                    created=False,
                    return_created=return_created,
                ),
            ),
            "with caller_creations._lock:",
            "    creation = caller_creations.get_creation(_spell_id)",
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
                    value_expression="creation",
                    created=False,
                    return_created=return_created,
                ),
            ),
        ]
    if resolve_route_key == "spellspace":
        return [
            "creation = caller_creations.get_creation(_spell_id)",
            "if creation is not None:",
            _prefix_one_indent(
                _build_return_statement(
                    value_expression="creation",
                    created=False,
                    return_created=return_created,
                ),
            ),
            "with caller_creations._lock:",
            "    creation = caller_creations.get_creation(_spell_id)",
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
                    value_expression="creation",
                    created=False,
                    return_created=return_created,
                ),
            ),
        ]
    if resolve_route_key == "shared":
        return [
            "creation = _spell._owner_creations.get_creation(_spell_id)",
            "if creation is not None:",
            _prefix_one_indent(
                _build_return_statement(
                    value_expression="creation",
                    created=False,
                    return_created=return_created,
                ),
            ),
            "with _spell._lock:",
            "    creation = _spell._owner_creations.get_creation(_spell_id)",
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
                    value_expression="creation",
                    created=False,
                    return_created=return_created,
                ),
            ),
        ]
    if resolve_route_key == "lineage":
        # unique_per_conduit_lineage: one instance per lineage, stored in the
        # RESOLVING door's lineage-root creations (passed at runtime as
        # `root_creations`), not the binding owner's `_owner_creations`. Mirrors
        # the unique_per_conduit shape but on the root store + its lock.
        return [
            "creation = root_creations.get_creation(_spell_id)",
            "if creation is not None:",
            _prefix_one_indent(
                _build_return_statement(
                    value_expression="creation",
                    created=False,
                    return_created=return_created,
                ),
            ),
            "with root_creations._lock:",
            "    creation = root_creations.get_creation(_spell_id)",
            "    if creation is None:",
        ] + _indent_lines(
            _build_no_overrides_create_lines(
                caller_creations_lock_held=False,
                return_created=return_created,
                owner_creations_expr="root_creations",
            ),
            2,
        ) + [
            _prefix_one_indent(
                _build_return_statement(
                    value_expression="creation",
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
    Build the route-specific emitted body for override-aware execution.

    The returned source lines become the inner runtime body for the selected
    existence route when override payloads are permitted. This is where the
    generated program decides whether a route can override an existing instance,
    whether it must create under a lock, and what error path should be emitted
    for invalid override usage.
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
                "creation = caller_creations.get_creation(_spell_id)",
                "if creation is not None:",
                "    raise _MeldExecutionError(",
                "        spell_id=_spell.spell_index.current,",
                "        spell_name=_spell.spell_name,",
                "        message=_existing_override_message,",
                "    )",
                "with caller_creations._lock:",
                "    creation = caller_creations.get_creation(_spell_id)",
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
            "creation = caller_creations.get_creation(_spell_id)",
            "if creation is not None:",
            "    if overrides is not None:",
            "        raise _MeldExecutionError(",
            "            spell_id=_spell.spell_index.current,",
            "            spell_name=_spell.spell_name,",
            "            message=_existing_override_message,",
            "        )",
            _prefix_one_indent(
                _build_return_statement(
                    value_expression="creation",
                    created=False,
                    return_created=return_created,
                ),
            ),
            "with caller_creations._lock:",
            "    creation = caller_creations.get_creation(_spell_id)",
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
                    value_expression="creation",
                    created=False,
                    return_created=return_created,
                ),
            ),
        ]
    if resolve_route_key == "spellspace":
        if not overrides_maybe_none:
            return [
                "creation = caller_creations.get_creation(_spell_id)",
                "if creation is not None:",
                "    raise _MeldExecutionError(",
                "        spell_id=_spell.spell_index.current,",
                "        spell_name=_spell.spell_name,",
                "        message=_existing_override_message,",
                "    )",
                "with caller_creations._lock:",
                "    creation = caller_creations.get_creation(_spell_id)",
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
            "creation = caller_creations.get_creation(_spell_id)",
            "if creation is not None:",
            "    if overrides is not None:",
            "        raise _MeldExecutionError(",
            "            spell_id=_spell.spell_index.current,",
            "            spell_name=_spell.spell_name,",
            "            message=_existing_override_message,",
            "        )",
            _prefix_one_indent(
                _build_return_statement(
                    value_expression="creation",
                    created=False,
                    return_created=return_created,
                ),
            ),
            "with caller_creations._lock:",
            "    creation = caller_creations.get_creation(_spell_id)",
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
                    value_expression="creation",
                    created=False,
                    return_created=return_created,
                ),
            ),
        ]
    if resolve_route_key == "shared":
        if not overrides_maybe_none:
            return [
                "creation = _spell._owner_creations.get_creation(_spell_id)",
                "if creation is not None:",
                "    raise _MeldExecutionError(",
                "        spell_id=_spell.spell_index.current,",
                "        spell_name=_spell.spell_name,",
                "        message=_existing_override_message,",
                "    )",
                "with _spell._lock:",
                "    creation = _spell._owner_creations.get_creation(_spell_id)",
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
            "creation = _spell._owner_creations.get_creation(_spell_id)",
            "if creation is not None:",
            "    if overrides is not None:",
                "        raise _MeldExecutionError(",
            "            spell_id=_spell.spell_index.current,",
            "            spell_name=_spell.spell_name,",
            "            message=_existing_override_message,",
            "        )",
            _prefix_one_indent(
                _build_return_statement(
                    value_expression="creation",
                    created=False,
                    return_created=return_created,
                ),
            ),
            "with _spell._lock:",
            "    creation = _spell._owner_creations.get_creation(_spell_id)",
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
                    value_expression="creation",
                    created=False,
                    return_created=return_created,
                ),
            ),
        ]
    if resolve_route_key == "lineage":
        # Lineage override lane: same shape as the shared override lane but on the
        # resolving door's lineage-root store (`root_creations`) + its lock,
        # instead of the binding owner's `_owner_creations`.
        if not overrides_maybe_none:
            return [
                "creation = root_creations.get_creation(_spell_id)",
                "if creation is not None:",
                "    raise _MeldExecutionError(",
                "        spell_id=_spell.spell_index.current,",
                "        spell_name=_spell.spell_name,",
                "        message=_existing_override_message,",
                "    )",
                "with root_creations._lock:",
                "    creation = root_creations.get_creation(_spell_id)",
                "    if creation is None:",
                "        instance = _execute_with_overrides(caller_creations, overrides, False, root_creations)",
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
            "creation = root_creations.get_creation(_spell_id)",
            "if creation is not None:",
            "    if overrides is not None:",
            "        raise _MeldExecutionError(",
            "            spell_id=_spell.spell_index.current,",
            "            spell_name=_spell.spell_name,",
            "            message=_existing_override_message,",
            "        )",
            _prefix_one_indent(
                _build_return_statement(
                    value_expression="creation",
                    created=False,
                    return_created=return_created,
                ),
            ),
            "with root_creations._lock:",
            "    creation = root_creations.get_creation(_spell_id)",
            "    if creation is None:",
            "        instance = _execute_with_overrides(caller_creations, overrides, False, root_creations)",
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
                    value_expression="creation",
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
        owner_creations_expr: str = "_spell._owner_creations",
) -> Sequence[str]:
    """
    Build the emitted call block for the no-overrides creation executor.

    This helper generates the shared snippet used by multiple routes when they
    fall through to actual creation work rather than returning an existing
    instance.
    """
    return [
        "instance = _no_overrides_executor(",
        "    caller_creations,",
        f"    {owner_creations_expr},",
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
    Build the final emitted return statement for one route branch.

    The helper centralizes the difference between instance-only lanes and
    `(instance, created)` hook lanes so branch builders do not duplicate that
    formatting logic.
    """
    if return_created:
        return f"return {value_expression}, {created}"
    return f"return {value_expression}"


def _prefix_one_indent(line: str) -> str:
    """
    Prefix one emitted source line with one indentation level.

    This helper exists because many of the emitted route builders need to splice
    generated single lines into larger nested source blocks.
    """
    return f"    {line}"


def _prefix_two_indent(line: str) -> str:
    """
    Prefix one emitted source line with two indentation levels.

    This is the two-level companion to `_prefix_one_indent` for generated code
    that must be nested inside a lock branch or other multi-level emitted block.
    """
    return f"        {line}"


def _indent_lines(lines: Sequence[str], level: int) -> list[str]:
    """
    Indent a sequence of emitted source lines by the requested level.

    These small formatting helpers exist because the file assembles Python
    source programmatically; keeping indentation generation centralized reduces
    copy-paste mistakes across the emitted template builders.
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
# unique_per_conduit_lineage: one instance per lineage, stored in the resolving
# door's lineage-root creations (`root_creations`), not the binding owner's
# `_owner_creations`. Lineage is never fast-transient (only `many` is).
_TEMPLATE_LINEAGE_OVERRIDES_ONLY = (
    _compile_creation_context_overrides_only_template(
        resolve_route_key="lineage",
        return_created=True,
    )
)
_TEMPLATE_LINEAGE_INSTANCE_OVERRIDES_ONLY = (
    _compile_creation_context_overrides_only_template(
        resolve_route_key="lineage",
        return_created=False,
    )
)
_TEMPLATE_LINEAGE_NO_OVERRIDES_ONLY = (
    _compile_creation_context_no_overrides_only_template(
        resolve_route_key="lineage",
        fast_transient_no_overrides_enabled=False,
        return_created=True,
    )
)
_TEMPLATE_LINEAGE_INSTANCE_NO_OVERRIDES_ONLY = (
    _compile_creation_context_no_overrides_only_template(
        resolve_route_key="lineage",
        fast_transient_no_overrides_enabled=False,
        return_created=False,
    )
)


_OVERRIDES_ONLY_INSTANCE_TEMPLATE_BY_ROUTE: dict[
    str,
    Callable[..., Callable[..., Any]],
] = {
    "existing_creation": _TEMPLATE_EXISTING_INSTANCE_OVERRIDES_ONLY,
    "many": _TEMPLATE_MANY_INSTANCE_OVERRIDES_ONLY,
    "unique_per_conduit": _TEMPLATE_UNIQUE_PER_CONDUIT_INSTANCE_OVERRIDES_ONLY,
    "spellspace": _TEMPLATE_SPELLSPACE_INSTANCE_OVERRIDES_ONLY,
    "shared": _TEMPLATE_SHARED_INSTANCE_OVERRIDES_ONLY,
    "lineage": _TEMPLATE_LINEAGE_INSTANCE_OVERRIDES_ONLY,
}

_OVERRIDES_ONLY_HOOKS_TEMPLATE_BY_ROUTE: dict[
    str,
    Callable[..., Callable[..., Any]],
] = {
    "existing_creation": _TEMPLATE_EXISTING_OVERRIDES_ONLY,
    "many": _TEMPLATE_MANY_OVERRIDES_ONLY,
    "unique_per_conduit": _TEMPLATE_UNIQUE_PER_CONDUIT_OVERRIDES_ONLY,
    "spellspace": _TEMPLATE_SPELLSPACE_OVERRIDES_ONLY,
    "shared": _TEMPLATE_SHARED_OVERRIDES_ONLY,
    "lineage": _TEMPLATE_LINEAGE_OVERRIDES_ONLY,
}

_NO_OVERRIDES_ONLY_INSTANCE_TEMPLATE_BY_ROUTE_AND_FAST: dict[
    tuple[str, bool],
    Callable[..., Callable[..., Any]],
] = {
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
    ("lineage", False): _TEMPLATE_LINEAGE_INSTANCE_NO_OVERRIDES_ONLY,
    ("lineage", True): _TEMPLATE_LINEAGE_INSTANCE_NO_OVERRIDES_ONLY,
}

_NO_OVERRIDES_ONLY_HOOKS_TEMPLATE_BY_ROUTE_AND_FAST: dict[
    tuple[str, bool],
    Callable[..., Callable[..., Any]],
] = {
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
    ("lineage", False): _TEMPLATE_LINEAGE_NO_OVERRIDES_ONLY,
    ("lineage", True): _TEMPLATE_LINEAGE_NO_OVERRIDES_ONLY,
}
