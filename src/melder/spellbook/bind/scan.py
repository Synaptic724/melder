from dataclasses import dataclass
from types import ModuleType
from typing import Any, Callable, Optional, Sequence

# Melder Imports
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.spellbook.existence.existence import Existence
from melder.utilities.interfaces.interfaces import ISpellbook

_SCAN_BIND_ATTR = "__melder_scan_bind__"


def _normalize_hooks(
        hook_name: str,
        hooks: Optional[Sequence[Callable[..., Any]]],
) -> Optional[tuple[Callable[..., Any], ...]]:
    """
    Internal

    Purpose:
        Normalize hook sequences for scan_bind metadata storage.
    Contract:
        - Accepts None, list, or tuple values.
        - Ensures each element is callable.
        - Returns hooks as an immutable tuple to prevent accidental mutation.
    Args:
        hook_name (str): The hook key being normalized (for error messaging).
        hooks (Optional[Sequence[Callable[..., Any]]]): Hook list/tuple or None.
    Returns:
        Optional[tuple[Callable[..., Any], ...]]:
            Tuple of hooks if provided; otherwise None.
    Raises:
        TypeError: If hooks is not a list/tuple or contains a non-callable.
    """
    if hooks is None:
        return None
    if not isinstance(hooks, (list, tuple)):
        raise TypeError(f"{hook_name} must be a list or tuple of callables.")
    for hook in hooks:
        if not callable(hook):
            raise TypeError(f"{hook_name} must contain only callables.")
    return tuple(hooks)


@dataclass(frozen=True)
class ScanBindMetadata:
    """
    Internal

    Purpose:
        Store explicit binding metadata for scan_bind-decorated objects.
    Contract:
        - Carries all inputs required to call Spellbook.bind.
        - Hook lists are stored as tuples and materialized into lists when used.
        - Metadata is immutable once created.
    """
    existence: Existence | str
    permissions: Permissions | str
    spellframe: Any | None
    binding_name: str | None
    pre_hooks: tuple[Callable[..., Any], ...] | None
    activation_hooks: tuple[Callable[..., Any], ...] | None
    post_hooks: tuple[Callable[..., Any], ...] | None

    def to_bind_kwargs(self) -> dict[str, Any]:
        """
        Internal

        Purpose:
            Build hook kwargs for Spellbook.bind without emitting None values.
        Contract:
            - Returns a dict containing only hook keys that were provided.
            - Hook tuples are copied into lists for Spellbook consumption.
        Returns:
            dict[str, Any]: Keyword arguments for Spellbook.bind hooks.
        """
        kwargs: dict[str, Any] = {}
        if self.pre_hooks is not None:
            kwargs["pre_hooks"] = list(self.pre_hooks)
        if self.activation_hooks is not None:
            kwargs["activation_hooks"] = list(self.activation_hooks)
        if self.post_hooks is not None:
            kwargs["post_hooks"] = list(self.post_hooks)
        return kwargs


def scan_bind(
        *,
        existence: Existence | str,
        permissions: Permissions | str,
        spellframe: Any = None,
        binding_name: str | None = None,
        pre_hooks: Optional[Sequence[Callable[..., Any]]] = None,
        activation_hooks: Optional[Sequence[Callable[..., Any]]] = None,
        post_hooks: Optional[Sequence[Callable[..., Any]]] = None,
) -> Callable[[Any], Any]:
    """
    Public API

    Attaches explicit binding metadata to a class/function for module scanning.

    This decorator does **not** bind anything by itself. It only stores the
    metadata needed by `Scan.scan_module(...)` or `Spellbook.scan(...)`.

    Args:
        existence (Existence | str):
            Explicit lifecycle scope for the spell (required).
        permissions (Permissions | str):
            Explicit permissions for the spell (required).
        spellframe (Any, optional):
            Optional spellframe/Protocol grouping key.
        binding_name (Optional[str]):
            Optional binding name for disambiguation.
        pre_hooks (Optional[Sequence[Callable[..., Any]]]):
            Optional pre-activation hooks.
        activation_hooks (Optional[Sequence[Callable[..., Any]]]):
            Optional activation hooks.
        post_hooks (Optional[Sequence[Callable[..., Any]]]):
            Optional post-activation hooks.

    Returns:
        Callable[[Any], Any]: A decorator that tags the target object.

    Raises:
        ValueError: If `existence` or `permissions` is None.
        TypeError: If any hook list is not a list/tuple of callables.
    """
    if existence is None:
        raise ValueError("scan_bind requires an explicit existence value.")
    if permissions is None:
        raise ValueError("scan_bind requires an explicit permissions value.")

    pre_hooks_tuple = _normalize_hooks("pre_hooks", pre_hooks)
    activation_hooks_tuple = _normalize_hooks("activation_hooks", activation_hooks)
    post_hooks_tuple = _normalize_hooks("post_hooks", post_hooks)

    def decorator(obj: Any) -> Any:
        """
        Internal

        Purpose:
            Attach ScanBindMetadata to the decorated object.
        Contract:
            - Stores metadata under a reserved attribute.
            - Returns the original object unchanged otherwise.
        Args:
            obj (Any): The object being decorated.
        Returns:
            Any: The original object.
        """
        metadata = ScanBindMetadata(
            existence=existence,
            permissions=permissions,
            spellframe=spellframe,
            binding_name=binding_name,
            pre_hooks=pre_hooks_tuple,
            activation_hooks=activation_hooks_tuple,
            post_hooks=post_hooks_tuple,
        )
        setattr(obj, _SCAN_BIND_ATTR, metadata)
        return obj

    return decorator


class Scan:
    """
    Public API

    Module-only scanner that binds objects decorated with `scan_bind`.

    Purpose:
        Provide an explicit execution step that reads scan_bind metadata and
        delegates binding to an owning Spellbook instance.
    Contract:
        - Only scans a single, user-supplied module (no package traversal).
        - Rejects re-exports: the object's ``__module__`` must match the module name.
        - Delegates all validation to `Spellbook.bind`.
    """
    __slots__ = ("_spellbook",)

    def __init__(self, spellbook: ISpellbook) -> None:
        """
        Initialize a Scan helper bound to a specific Spellbook.

        Args:
            spellbook (ISpellbook): The Spellbook used for binding.
        Raises:
            ValueError: If spellbook is None.
        """
        if spellbook is None:
            raise ValueError("Scan requires a valid Spellbook instance.")
        self._spellbook = spellbook

    def scan_module(self, module: ModuleType) -> list[str]:
        """
        Public API

        Scan a module for `scan_bind` metadata and bind all marked objects.

        Args:
            module (ModuleType): The module to scan for decorated targets.
        Returns:
            list[str]: Spell IDs bound during the scan, in module dict order.
        Raises:
            TypeError: If `module` is not a module or metadata is invalid.
            ValueError: If a decorated object is not owned by the module.
            RuntimeError: Propagated from Spellbook.bind on binding errors.
        """
        if not isinstance(module, ModuleType):
            raise TypeError("scan_module requires a Python module object.")

        module_name = module.__name__
        spell_ids: list[str] = []

        for attr_name, obj in vars(module).items():
            metadata = getattr(obj, _SCAN_BIND_ATTR, None)
            if metadata is None:
                continue
            if not isinstance(metadata, ScanBindMetadata):
                raise TypeError(
                    f"scan_bind metadata for '{attr_name}' is invalid or corrupted."
                )

            obj_module = getattr(obj, "__module__", None)
            if obj_module != module_name:
                raise ValueError(
                    "scan_module rejects re-exports. "
                    f"Object '{attr_name}' originates from module '{obj_module}', "
                    f"not '{module_name}'."
                )

            bind_kwargs = metadata.to_bind_kwargs()
            spell_id = self._spellbook.bind(
                spell=obj,
                existence=metadata.existence,
                permissions=metadata.permissions,
                spellframe=metadata.spellframe,
                binding_name=metadata.binding_name,
                **bind_kwargs,
            )
            spell_ids.append(spell_id)

        return spell_ids


__all__ = ("scan_bind", "Scan", "ScanBindMetadata")
