"""
Top-level creation-context doors: a runtime overlay prototype (melder_0, 2026-09-30; option A of
tickets/tasks/2026-09-30_map_remaining_melder_gauntlet_gains_task.md).

Purpose:
    Melder builds each spell's creation-context door by calling a template function that returns a nested closure
    over that spell's bindings (`creation_runtime_door_compiler._build_creation_context_template_source`). On
    free-threaded CPython 3.14 a closure is not deferred-refcounted, and its cells are ordinary objects, so every
    door call pays atomic reference-count operations on objects shared by all threads. This overlay emits the same
    door bodies as TOP-LEVEL functions whose bindings live in a per-spell globals dict. CPython 3.14t then marks
    the function deferred by itself (its code has no CO_NESTED flag), loading it from a CreationContext slot
    pushes a borrowed stackref, and there are no cells to copy into the frame.

Contract:
    - `install(module)` replaces every entry of the door compiler module's four template dicts with a
      `TopLevelDoorTemplate` built from the module's own route-body builders (`_build_no_overrides_lines`,
      `_build_with_overrides_lines`), so the door bodies, messages and return shapes are unchanged. It must run
      before any Spellbook hydrates a creation context; `uninstall(module)` puts the originals back.
    - The repository tree is never modified: this is an in-process overlay for measurement.
    - Every door gets its own code-object copy, so each LOAD_GLOBAL specializes against its own globals dict.

Threading:
    `install`/`uninstall` mutate module dicts and are meant to run once, before worker threads exist. Built doors
    are immutable after construction and safe to call from any thread, like the closures they replace.
"""
import builtins
import types
from typing import Any, Callable, Dict, List, Sequence, Tuple


class TopLevelDoorTemplate:
    """
    Door factory with the compiler's template contract: `template(**bindings) -> door`.

    Purpose:
        Stand in for one emitted template function. Instead of returning a nested closure, it returns a new
        top-level function built from one route body's code object and a globals dict holding the spell's bindings.

    Contract:
        - `__call__` never mutates the template; each call returns a new function with its own code copy and its
          own globals dict (`bindings` plus `__builtins__`).
        - The returned function is not nested, so free-threaded CPython 3.14 gives it deferred reference counting.

    Threading:
        Read-only after construction; concurrent calls are safe.
    """

    __slots__ = ("_code", "_name")

    def __init__(self, code: types.CodeType, name: str) -> None:
        """
        Keep one compiled route body.

        Args:
            code: Code object of the top-level door function for one route and lane.
            name: Function name given to every door built from this template.
        """
        self._code: types.CodeType = code
        self._name: str = name

    def __call__(self, **bindings: Any) -> Callable[..., Any]:
        """
        Build one spell's door.

        Args:
            **bindings: The spell-static values the compiler passes to its templates (`_spell`, `_spell_id`,
                `_owner_creations`, the executors, the error types and the messages).

        Returns:
            Callable[..., Any]: A top-level function over a private globals dict holding `bindings`.
        """
        namespace: Dict[str, Any] = dict(bindings)
        namespace["__builtins__"] = builtins
        return types.FunctionType(self._code.replace(), namespace, self._name)


def _compile_door(
        module: Any,
        *,
        lines: Sequence[str],
        callable_name: str,
        signature: str,
        source_name: str,
) -> TopLevelDoorTemplate:
    """
    Compile one route body as a top-level function and wrap its code in a template.

    Args:
        module: The door compiler module (for its `_indent_lines` helper).
        lines: Route body lines from the module's own builders.
        callable_name: Door function name (the same name the closures carry today).
        signature: Door parameters, `meld` or `meld, overrides`.
        source_name: Filename shown in tracebacks.

    Returns:
        TopLevelDoorTemplate: The factory that builds this route's doors.
    """
    source = "\n".join([f"def {callable_name}({signature}):", *module._indent_lines(lines, 1)])
    scratch: Dict[str, Any] = {"__builtins__": builtins}
    exec(compile(source, source_name, "exec"), scratch)
    return TopLevelDoorTemplate(scratch[callable_name].__code__, callable_name)


def _routes() -> Tuple[str, ...]:
    """
    Return the resolve routes the door compiler supports (its four dicts are keyed by these).

    Returns:
        Tuple[str, ...]: Route keys.
    """
    return ("existing_creation", "many", "unique_per_conduit", "spellspace", "unique", "lineage", "cluster")


def build_templates(module: Any) -> Dict[str, Dict[Any, TopLevelDoorTemplate]]:
    """
    Build top-level templates for all four door families of the compiler module.

    Args:
        module: The door compiler module.

    Returns:
        Dict[str, Dict[Any, TopLevelDoorTemplate]]: Replacement dicts keyed like the module's own:
            no_overrides_instance and no_overrides_hooks by (route, fast); overrides_instance and
            overrides_hooks by route.
    """
    no_instance: Dict[Any, TopLevelDoorTemplate] = {}
    no_hooks: Dict[Any, TopLevelDoorTemplate] = {}
    ov_instance: Dict[Any, TopLevelDoorTemplate] = {}
    ov_hooks: Dict[Any, TopLevelDoorTemplate] = {}
    for route in _routes():
        for fast in (False, True):
            use_fast = route == "many" and fast
            for return_created, target in ((False, no_instance), (True, no_hooks)):
                lines = module._build_no_overrides_lines(
                    resolve_route_key=route,
                    fast_transient_no_overrides_enabled=use_fast,
                    return_created=return_created,
                )
                target[(route, fast)] = _compile_door(
                    module,
                    lines=lines,
                    callable_name="_creation_context_execute_no_overrides_only",
                    signature="meld",
                    source_name=f"<creation_context_door_no_overrides:{route}:{int(use_fast)}:{int(return_created)}>",
                )
        for return_created, target in ((False, ov_instance), (True, ov_hooks)):
            lines = module._build_with_overrides_lines(resolve_route_key=route, return_created=return_created)
            target[route] = _compile_door(
                module,
                lines=lines,
                callable_name="_creation_context_execute_overrides_only",
                signature="meld, overrides",
                source_name=f"<creation_context_door_overrides:{route}:{int(return_created)}>",
            )
    return {
        "_NO_OVERRIDES_ONLY_INSTANCE_TEMPLATE_BY_ROUTE_AND_FAST": no_instance,
        "_NO_OVERRIDES_ONLY_HOOKS_TEMPLATE_BY_ROUTE_AND_FAST": no_hooks,
        "_OVERRIDES_ONLY_INSTANCE_TEMPLATE_BY_ROUTE": ov_instance,
        "_OVERRIDES_ONLY_HOOKS_TEMPLATE_BY_ROUTE": ov_hooks,
    }


def install(module: Any) -> Dict[str, Dict[Any, Any]]:
    """
    Swap the compiler module's template dict entries for top-level door templates.

    Args:
        module: The door compiler module
            (`melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.
            creation_runtime_door_compiler`).

    Returns:
        Dict[str, Dict[Any, Any]]: The original entries per dict name, for `uninstall`.

    Raises:
        AssertionError: A replacement dict does not cover exactly the module dict's keys.
    """
    replacements = build_templates(module)
    originals: Dict[str, Dict[Any, Any]] = {}
    for dict_name, replacement in replacements.items():
        target = getattr(module, dict_name)
        if set(target) != set(replacement):
            raise AssertionError(f"{dict_name}: keys differ: {sorted(set(target) ^ set(replacement))}")
        originals[dict_name] = dict(target)
        target.update(replacement)
    return originals


def uninstall(module: Any, originals: Dict[str, Dict[Any, Any]]) -> None:
    """
    Put the original template entries back.

    Args:
        module: The door compiler module.
        originals: What `install` returned.
    """
    for dict_name, entries in originals.items():
        getattr(module, dict_name).update(entries)


def door_module() -> Any:
    """
    Import and return the door compiler module from the `melder` package on sys.path.

    Returns:
        Any: The module object.
    """
    import importlib
    return importlib.import_module(
        "melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.creation_runtime_door_compiler"
    )


def describe_doors(executors: List[Callable[..., Any]]) -> Dict[str, int]:
    """
    Count how many door functions are nested, carry cells, or are deferred (diagnostic; reads object headers).

    Args:
        executors: Door functions taken from creation contexts.

    Returns:
        Dict[str, int]: total, nested, with_cells and deferred counts.
    """
    import ctypes
    import inspect
    counts = {"total": 0, "nested": 0, "with_cells": 0, "deferred": 0}
    for function in executors:
        counts["total"] += 1
        if function.__code__.co_flags & inspect.CO_NESTED:
            counts["nested"] += 1
        if function.__closure__:
            counts["with_cells"] += 1
        if ctypes.c_uint8.from_address(id(function) + 11).value & 64:
            counts["deferred"] += 1
    return counts
