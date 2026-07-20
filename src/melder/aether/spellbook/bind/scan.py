from dataclasses import dataclass
from types import ModuleType
from typing import TYPE_CHECKING, Any, Callable, Optional, Sequence

if TYPE_CHECKING:
    from melder.aether.spellbook.spellbook import Spellbook



# Melder Imports
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.spellbook.existence.existence import Existence
from melder.utilities.general_base.cleanable import Cleanable

_SCAN_BIND_ATTR = "__melder_scan_bind__"


def _normalize_hooks(
        hook_name: str,
        hooks: Optional[Sequence[Callable[..., Any]]],
) -> Optional[tuple[Callable[..., Any], ...]]:
    """
    Normalize hook sequences for `scan_bind` metadata storage.

    Purpose:
        Convert user-facing hook inputs into the stable shape stored inside
        `ScanBindMetadata`.

    Contract:
        - Accepts None, list, or tuple values.
        - Ensures each element is callable before metadata is attached.
        - Returns hooks as an immutable tuple so decorator-time metadata cannot
          be mutated accidentally after decoration.
        - Preserves hook ordering exactly as supplied by the caller.
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


@dataclass(frozen=True, slots=True)
class ScanBindMetadata:
    """
    Frozen payload describing how a decorated object should be bound later.

    Purpose:
        Capture the exact bind-time policy, lifecycle, spellframe, and hook
        configuration declared by `scan_bind(...)` without performing
        registration immediately.

    Contract:
        - Carries all inputs required to call `Spellbook.bind` during a later
          module scan.
        - Preserves `Existence | str` and `Permissions | str` values as
          provided so later spellbook code can apply the same normalization path
          used by direct binding.
        - Hook collections are stored as tuples at rest and materialized into
          fresh lists only when handed to `Spellbook.bind`.
        - Metadata is immutable once created so decorated objects carry a
          stable registration contract.

    Threading:
        Immutable once created; safe to share across threads.

    Registration:
        MELDER KERNEL - guarded. Attached to decorated objects by
        `scan_bind(...)`.

    Subsystem Context:
        The frozen payload a `scan_bind` decoration leaves behind, consumed by
        `Scan` and replayed into `Spellbook.bind`.

    System Context:
        Preserving `Existence | str` and `Permissions | str` AS PROVIDED rather
        than normalizing at decoration time is the subtle correctness decision.
        Normalizing early would run enum conversion at import time, before the
        spellbook that will interpret the values exists - and would bake in a
        normalization the direct-bind path might later change. Deferring means
        the deferred and direct paths share exactly one normalization.
        Immutability is what makes a decorated object carry a STABLE
        registration contract: the metadata is read at scan time, potentially
        long after decoration, and something mutable in between would let a
        module's declared bindings drift from what its source says.
        Hooks stored as tuples at rest and materialized into FRESH lists only
        when handed to `bind` is the same discipline applied to collections -
        the frozen payload cannot be mutated through a list a caller kept.
    """
    existence: Existence | str
    permissions: Permissions | str
    spellframe: Any | None
    binding_name: str | None
    profile: str
    pre_hooks: tuple[Callable[..., Any], ...] | None
    activation_hooks: tuple[Callable[..., Any], ...] | None
    post_hooks: tuple[Callable[..., Any], ...] | None

    def to_bind_kwargs(self) -> dict[str, Any]:
        """
        Build the keyword payload consumed by `Spellbook.bind`.

        Purpose:
            Translate frozen scan metadata into the mutable hook/profile kwargs
            expected by the real binding pipeline.
        Contract:
            - Returns a dict containing only hook keys that were explicitly
              provided.
            - Hook tuples are copied into new lists so later bind-time mutation
              cannot alias back into stored metadata.
            - Always includes `profile`, because that value is part of the
              public scan-bind contract even when no hooks are supplied.
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
        kwargs["profile"] = self.profile
        return kwargs


def scan_bind(
        *,
        existence: Existence | str,
        permissions: Permissions | str,
        spellframe: Any = None,
        binding_name: str | None = None,
        profile: str = "general",
        pre_hooks: Optional[Sequence[Callable[..., Any]]] = None,
        activation_hooks: Optional[Sequence[Callable[..., Any]]] = None,
        post_hooks: Optional[Sequence[Callable[..., Any]]] = None,
) -> Callable[[Any], Any]:
    """
    Attaches explicit binding metadata to a class/function for module scanning.

    This decorator does **not** bind anything by itself. It only stores the
    metadata needed by `Scan.scan_module(...)` or `Spellbook.scan(...)`.

    Runtime model:
        - decoration time: capture binding intent only
        - scan time: verify module ownership and re-export rules
        - bind time: delegate to `Spellbook.bind` for actual registration

    Contract:
        - Returns a decorator that leaves the target object otherwise unchanged.
        - Stores one immutable `ScanBindMetadata` payload on the decorated
          object under the reserved scan-bind attribute.
        - Does not register anything, allocate `Spell` objects, or talk to a
          `Spellbook` directly.
        - Hook values are validated immediately so invalid metadata does not sit
          silently on the object until module scan time.

    Args:
        existence (Existence | str):
            Explicit lifecycle scope for the spell (required).
        permissions (Permissions | str):
            Explicit permissions for the spell (required).
        spellframe (Any, optional):
            Optional spellframe/Protocol grouping key.
        binding_name (Optional[str]):
            Optional binding name for disambiguation.
        profile (str):
            Spell profile family to attach after bind completion.
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
        Attach `ScanBindMetadata` to the decorated object.

        Contract:
            - Stores metadata under the reserved scan-bind attribute.
            - Returns the original object unchanged so the decorator is
              transparent to normal import and runtime use.
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
            profile=profile,
            pre_hooks=pre_hooks_tuple,
            activation_hooks=activation_hooks_tuple,
            post_hooks=post_hooks_tuple,
        )
        setattr(obj, _SCAN_BIND_ATTR, metadata)
        return obj

    return decorator


class Scan(Cleanable):
    """
    Public API

    Module-only scanner that binds objects decorated with `scan_bind`.

    Purpose:
        Provide an explicit execution step that reads scan_bind metadata and
        delegates binding to an owning Spellbook instance.

    Contract:
        - Only scans a single, user-supplied module (no package traversal).
        - Rejects re-exports: the object's __module__`` must match the module name.
        - Delegates all validation to `Spellbook.bind`.

    Registration:
        MELDER KERNEL - guarded. Driven through `Spellbook.scan(...)`.

    Subsystem Context:
        The deferred-registration lane, paired with `ScanBindMetadata` (what a
        decorator recorded) and delegating every actual registration to
        `Spellbook.bind`.

    System Context:
        MODULE-ONLY, NO PACKAGE TRAVERSAL is a deliberate refusal of
        convenience. Recursive discovery would make what gets bound depend on
        filesystem layout and import side effects, so a refactor that moved a
        file could silently change a running system's spell set. Requiring an
        explicit module keeps registration a decision.
        REJECTING RE-EXPORTS via the `__module__` check closes the matching
        hole: without it, a module that imported a decorated class would bind it
        a second time under a different scan, producing duplicate registrations
        of one object. The test is ownership - a module binds only what it
        actually defines.
        Delegating ALL validation to `Spellbook.bind` means the deferred path
        and the direct path cannot diverge; there is one set of rules about what
        may become a spell, regardless of how it arrived.
    """
    __slots__ = tuple(Cleanable.__slots__) + ("_spellbook",)

    def __init__(self, spellbook: "Spellbook") -> None:
        """
        Initialize a Scan helper bound to a specific Spellbook.

        Args:
            spellbook (Spellbook): The Spellbook used for binding.
        Raises:
            ValueError: If spellbook is None.
        """
        super().__init__()
        if spellbook is None:
            raise ValueError("Scan requires a valid Spellbook instance.")
        self._spellbook = spellbook

    def cleanup(self) -> None:
        """
        Retire this scan helper and drop the owning Spellbook reference.

        Contract:
            - Idempotent.
            - Deletes the strong Spellbook reference.
            - Leaves future public calls to fail through `check_cleaned()`.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        del self._spellbook

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
        self.check_cleaned()
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
