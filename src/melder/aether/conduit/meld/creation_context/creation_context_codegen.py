from typing import Optional, Any, Callable, Sequence


def compile_creation_context_executor(
        *,
        resolve_route_key: str,
        mutation_override_enabled: bool,
        fast_transient_no_overrides_enabled: bool,
        spell: Any,
        spell_id: str,
        owner_creations: Any,
        no_overrides_executor: Optional[Callable[..., Any]],
        execute_with_overrides: Callable[..., Any],
        meld_execution_error_type: Any,
        spell_space_scope_error_type: Any,
) -> Callable[..., Any]:
    """
    Build one spell-bound CreationContext executor from precompiled templates.

    Purpose:
        Keep runtime hot paths generated via compile/exec while avoiding
        per-spell source compilation overhead.

    Contract:
        - Output callable signature:
          `(caller_creations, overrides=None) -> tuple[Any, bool]`.
        - `many` can use direct transient no-overrides lane.
        - Mutation-enabled contexts execute override lane for `overrides=None`.
    """
    use_fast_transient = bool(
        resolve_route_key == "many"
        and fast_transient_no_overrides_enabled
        and not mutation_override_enabled
    )
    template = _select_template(
        resolve_route_key=resolve_route_key,
        mutation_override_enabled=mutation_override_enabled,
        use_fast_transient=use_fast_transient,
        return_created=True,
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


def compile_creation_context_instance_executor(
        *,
        resolve_route_key: str,
        mutation_override_enabled: bool,
        fast_transient_no_overrides_enabled: bool,
        spell: Any,
        spell_id: str,
        owner_creations: Any,
        no_overrides_executor: Optional[Callable[..., Any]],
        execute_with_overrides: Callable[..., Any],
        meld_execution_error_type: Any,
        spell_space_scope_error_type: Any,
) -> Callable[..., Any]:
    """
    Build one spell-bound CreationContext executor that returns instance only.

    Purpose:
        Provide a tuple-free execution lane for no-hooks meld flow.

    Contract:
        - Output callable signature:
          `(caller_creations, overrides=None) -> Any`.
        - Uses the same existence/override routing as tuple-return executor.
    """
    use_fast_transient = bool(
        resolve_route_key == "many"
        and fast_transient_no_overrides_enabled
        and not mutation_override_enabled
    )
    template = _select_template(
        resolve_route_key=resolve_route_key,
        mutation_override_enabled=mutation_override_enabled,
        use_fast_transient=use_fast_transient,
        return_created=False,
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


def _select_template(
        *,
        resolve_route_key: str,
        mutation_override_enabled: bool,
        use_fast_transient: bool,
        return_created: bool,
) -> Callable[..., Any]:
    """
    Resolve one precompiled template factory by static spell shape.
    """
    if resolve_route_key == "existing_creation":
        if mutation_override_enabled:
            if return_created:
                return _TEMPLATE_EXISTING_MUTATION
            return _TEMPLATE_EXISTING_MUTATION_INSTANCE
        if return_created:
            return _TEMPLATE_EXISTING_NO_MUTATION
        return _TEMPLATE_EXISTING_NO_MUTATION_INSTANCE
    if resolve_route_key == "many":
        if mutation_override_enabled:
            if return_created:
                return _TEMPLATE_MANY_MUTATION
            return _TEMPLATE_MANY_MUTATION_INSTANCE
        if use_fast_transient:
            if return_created:
                return _TEMPLATE_MANY_NO_MUTATION_FAST
            return _TEMPLATE_MANY_NO_MUTATION_FAST_INSTANCE
        if return_created:
            return _TEMPLATE_MANY_NO_MUTATION
        return _TEMPLATE_MANY_NO_MUTATION_INSTANCE
    if resolve_route_key == "unique_per_conduit":
        if mutation_override_enabled:
            if return_created:
                return _TEMPLATE_UNIQUE_PER_CONDUIT_MUTATION
            return _TEMPLATE_UNIQUE_PER_CONDUIT_MUTATION_INSTANCE
        if return_created:
            return _TEMPLATE_UNIQUE_PER_CONDUIT_NO_MUTATION
        return _TEMPLATE_UNIQUE_PER_CONDUIT_NO_MUTATION_INSTANCE
    if resolve_route_key == "spellspace":
        if mutation_override_enabled:
            if return_created:
                return _TEMPLATE_SPELLSPACE_MUTATION
            return _TEMPLATE_SPELLSPACE_MUTATION_INSTANCE
        if return_created:
            return _TEMPLATE_SPELLSPACE_NO_MUTATION
        return _TEMPLATE_SPELLSPACE_NO_MUTATION_INSTANCE
    if resolve_route_key == "shared":
        if mutation_override_enabled:
            if return_created:
                return _TEMPLATE_SHARED_MUTATION
            return _TEMPLATE_SHARED_MUTATION_INSTANCE
        if return_created:
            return _TEMPLATE_SHARED_NO_MUTATION
        return _TEMPLATE_SHARED_NO_MUTATION_INSTANCE
    raise RuntimeError(
        f"Unsupported CreationContext resolve route key: {resolve_route_key}"
    )


def _compile_creation_context_template(
        *,
        resolve_route_key: str,
        mutation_override_enabled: bool,
        fast_transient_no_overrides_enabled: bool,
        return_created: bool,
) -> Callable[..., Any]:
    """
    Compile one template factory that binds static context dependencies.
    """
    no_overrides_lines = _build_no_overrides_lines(
        resolve_route_key=resolve_route_key,
        fast_transient_no_overrides_enabled=fast_transient_no_overrides_enabled,
        return_created=return_created,
    )
    with_overrides_lines = _build_with_overrides_lines(
        resolve_route_key=resolve_route_key,
        return_created=return_created,
    )
    source = _build_template_source(
        mutation_override_enabled=mutation_override_enabled,
        no_overrides_lines=no_overrides_lines,
        with_overrides_lines=with_overrides_lines,
    )
    local_namespace: dict[str, Any] = {}
    source_name = (
        "<creation_context_template:"
        f"{resolve_route_key}:"
        f"{int(mutation_override_enabled)}:"
        f"{int(fast_transient_no_overrides_enabled)}:"
        f"{int(return_created)}>"
    )
    try:
        exec(
            compile(source, source_name, "exec"),
            {},
            local_namespace,
        )
    except Exception as exc:
        raise RuntimeError(
            "Failed to compile CreationContext template source."
        ) from exc
    template = local_namespace.get("_creation_context_template")
    if callable(template):
        return template
    raise RuntimeError(
        "CreationContext template source did not define callable _creation_context_template."
    )


def _build_template_source(
        *,
        mutation_override_enabled: bool,
        no_overrides_lines: Sequence[str],
        with_overrides_lines: Sequence[str],
) -> str:
    """
    Build emitted source for one CreationContext template factory.
    """
    lines = [
        "def _creation_context_template(",
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
        "    ):",
        "    def _creation_context_execute(caller_creations, overrides=None):",
    ]
    if mutation_override_enabled:
        lines.extend(_indent_lines(with_overrides_lines, 2))
    else:
        lines.append("        if overrides is None:")
        lines.extend(_indent_lines(no_overrides_lines, 3))
        lines.extend(_indent_lines(with_overrides_lines, 2))
    lines.append("    return _creation_context_execute")
    return "\n".join(lines)


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
                "instance = _no_overrides_executor(None)",
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
            "creation = caller_creations.get_spellspace_creation(spellspace.id, _spell_id)",
            "if creation is not None:",
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
) -> Sequence[str]:
    """
    Build with-overrides existence path source lines.
    """
    if resolve_route_key == "existing_creation":
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


_TEMPLATE_EXISTING_NO_MUTATION = _compile_creation_context_template(
    resolve_route_key="existing_creation",
    mutation_override_enabled=False,
    fast_transient_no_overrides_enabled=False,
    return_created=True,
)
_TEMPLATE_EXISTING_MUTATION = _compile_creation_context_template(
    resolve_route_key="existing_creation",
    mutation_override_enabled=True,
    fast_transient_no_overrides_enabled=False,
    return_created=True,
)
_TEMPLATE_MANY_NO_MUTATION = _compile_creation_context_template(
    resolve_route_key="many",
    mutation_override_enabled=False,
    fast_transient_no_overrides_enabled=False,
    return_created=True,
)
_TEMPLATE_MANY_NO_MUTATION_FAST = _compile_creation_context_template(
    resolve_route_key="many",
    mutation_override_enabled=False,
    fast_transient_no_overrides_enabled=True,
    return_created=True,
)
_TEMPLATE_MANY_MUTATION = _compile_creation_context_template(
    resolve_route_key="many",
    mutation_override_enabled=True,
    fast_transient_no_overrides_enabled=False,
    return_created=True,
)
_TEMPLATE_UNIQUE_PER_CONDUIT_NO_MUTATION = _compile_creation_context_template(
    resolve_route_key="unique_per_conduit",
    mutation_override_enabled=False,
    fast_transient_no_overrides_enabled=False,
    return_created=True,
)
_TEMPLATE_UNIQUE_PER_CONDUIT_MUTATION = _compile_creation_context_template(
    resolve_route_key="unique_per_conduit",
    mutation_override_enabled=True,
    fast_transient_no_overrides_enabled=False,
    return_created=True,
)
_TEMPLATE_SPELLSPACE_NO_MUTATION = _compile_creation_context_template(
    resolve_route_key="spellspace",
    mutation_override_enabled=False,
    fast_transient_no_overrides_enabled=False,
    return_created=True,
)
_TEMPLATE_SPELLSPACE_MUTATION = _compile_creation_context_template(
    resolve_route_key="spellspace",
    mutation_override_enabled=True,
    fast_transient_no_overrides_enabled=False,
    return_created=True,
)
_TEMPLATE_SHARED_NO_MUTATION = _compile_creation_context_template(
    resolve_route_key="shared",
    mutation_override_enabled=False,
    fast_transient_no_overrides_enabled=False,
    return_created=True,
)
_TEMPLATE_SHARED_MUTATION = _compile_creation_context_template(
    resolve_route_key="shared",
    mutation_override_enabled=True,
    fast_transient_no_overrides_enabled=False,
    return_created=True,
)
_TEMPLATE_EXISTING_NO_MUTATION_INSTANCE = _compile_creation_context_template(
    resolve_route_key="existing_creation",
    mutation_override_enabled=False,
    fast_transient_no_overrides_enabled=False,
    return_created=False,
)
_TEMPLATE_EXISTING_MUTATION_INSTANCE = _compile_creation_context_template(
    resolve_route_key="existing_creation",
    mutation_override_enabled=True,
    fast_transient_no_overrides_enabled=False,
    return_created=False,
)
_TEMPLATE_MANY_NO_MUTATION_INSTANCE = _compile_creation_context_template(
    resolve_route_key="many",
    mutation_override_enabled=False,
    fast_transient_no_overrides_enabled=False,
    return_created=False,
)
_TEMPLATE_MANY_NO_MUTATION_FAST_INSTANCE = _compile_creation_context_template(
    resolve_route_key="many",
    mutation_override_enabled=False,
    fast_transient_no_overrides_enabled=True,
    return_created=False,
)
_TEMPLATE_MANY_MUTATION_INSTANCE = _compile_creation_context_template(
    resolve_route_key="many",
    mutation_override_enabled=True,
    fast_transient_no_overrides_enabled=False,
    return_created=False,
)
_TEMPLATE_UNIQUE_PER_CONDUIT_NO_MUTATION_INSTANCE = _compile_creation_context_template(
    resolve_route_key="unique_per_conduit",
    mutation_override_enabled=False,
    fast_transient_no_overrides_enabled=False,
    return_created=False,
)
_TEMPLATE_UNIQUE_PER_CONDUIT_MUTATION_INSTANCE = _compile_creation_context_template(
    resolve_route_key="unique_per_conduit",
    mutation_override_enabled=True,
    fast_transient_no_overrides_enabled=False,
    return_created=False,
)
_TEMPLATE_SPELLSPACE_NO_MUTATION_INSTANCE = _compile_creation_context_template(
    resolve_route_key="spellspace",
    mutation_override_enabled=False,
    fast_transient_no_overrides_enabled=False,
    return_created=False,
)
_TEMPLATE_SPELLSPACE_MUTATION_INSTANCE = _compile_creation_context_template(
    resolve_route_key="spellspace",
    mutation_override_enabled=True,
    fast_transient_no_overrides_enabled=False,
    return_created=False,
)
_TEMPLATE_SHARED_NO_MUTATION_INSTANCE = _compile_creation_context_template(
    resolve_route_key="shared",
    mutation_override_enabled=False,
    fast_transient_no_overrides_enabled=False,
    return_created=False,
)
_TEMPLATE_SHARED_MUTATION_INSTANCE = _compile_creation_context_template(
    resolve_route_key="shared",
    mutation_override_enabled=True,
    fast_transient_no_overrides_enabled=False,
    return_created=False,
)
