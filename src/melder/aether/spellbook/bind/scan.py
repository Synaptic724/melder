from types import MappingProxyType, ModuleType
from typing import TYPE_CHECKING, Any, Callable, ClassVar, Mapping, Optional, Sequence, Union

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


def _normalize_disposal_method_names(
        disposal_method_names: Optional[Sequence[str]],
) -> Optional[tuple[str, ...]]:
    """
    Normalize a per-target disposal group for `scan_bind` metadata storage.

    Purpose:
        Validate and snapshot the disposal candidates a decorator declares, so the
        group a later scan replays is exactly the group written at the decoration
        site.

    Contract:
        - Accepts None, list, or tuple values; None means "no per-target group".
        - Every element must be a `str` method name. A bare string is refused:
          `Spellbook.bind` would iterate it per character and silently match
          nothing.
        - Returns an immutable tuple that keeps the supplied order and any
          duplicates; Bind owns matching, de-duplication and the Book overlap and
          priority rules when the module is scanned.
        - An empty list or tuple is kept as an empty tuple. Like an omitted group,
          it leaves the Book's configured candidates in force; it never disables
          Book disposal.

    Args:
        disposal_method_names (Optional[Sequence[str]]): Per-target candidates or None.

    Returns:
        Optional[tuple[str, ...]]: Tuple of names if provided; otherwise None.

    Raises:
        TypeError: If the value is not None, a list or a tuple, or holds an element
            that is not a string.
    """
    if disposal_method_names is None:
        return None
    if not isinstance(disposal_method_names, (list, tuple)):
        raise TypeError(
            "disposal_method_names must be a list or tuple of method-name strings, got "
            f"{type(disposal_method_names).__name__}. Wrap a single name in a list: ['close']."
        )
    for method_name in disposal_method_names:
        if not isinstance(method_name, str):
            raise TypeError(
                "disposal_method_names must be a list or tuple of method-name strings; "
                f"found an element of type {type(method_name).__name__}."
            )
    return tuple(disposal_method_names)


def _normalize_spell_metadata(spell_metadata: Mapping[str, Any]) -> dict[str, Any]:
    """
    Validate and copy the application metadata a `scan_bind` declaration carries.

    Purpose:
        Keep application metadata from colliding with, or shadowing, an argument
        the bind pipeline takes natively, and decouple the stored entries from the
        caller's mapping.

    Contract:
        - Refuses every key in `ScanBindMetadata.RESERVED_SPELL_METADATA_KEYS`; the
          error names all offending keys, sorted, so one fix covers the
          declaration.
        - Returns a new dict with the same keys and the same value objects (a
          shallow copy): values are never copied, frozen or inspected.

    Args:
        spell_metadata (Mapping[str, Any]): Keyword metadata captured by `scan_bind`.

    Returns:
        dict[str, Any]: A shallow copy of the metadata.

    Raises:
        TypeError: If any key is reserved.
    """
    reserved = sorted(ScanBindMetadata.RESERVED_SPELL_METADATA_KEYS.intersection(spell_metadata))
    if reserved:
        raise TypeError(
            "scan_bind metadata keys are reserved by the bind pipeline and cannot carry "
            f"application metadata: {', '.join(reserved)}. Rename the key; native bind "
            "arguments cannot be supplied as metadata."
        )
    return dict(spell_metadata)


class ScanBindMetadata:
    """
    Frozen payload describing how a decorated object should be bound later.

    Purpose:
        Capture the exact bind-time policy, lifecycle, spellframe, capability,
        disposal, hook and application-metadata configuration declared by
        `scan_bind(...)` without performing registration immediately.

    Contract:
        - Carries all inputs required to call `Spellbook.bind` during a later
          module scan.
        - Preserves `Union[Existence, str]` and `Union[Permissions, str]` values
          as provided so later spellbook code can apply the same normalization
          path used by direct binding. `resolvable` is likewise stored exactly as
          given; Bind's strict bool check runs when the module is scanned.
        - Hook collections are stored as tuples at rest and materialized into
          fresh lists only when handed to `Spellbook.bind`.
        - Per-target disposal names are stored as a tuple (or None) and replayed
          unchanged; Bind resolves them against the Book's candidates.
        - Application metadata is stored as a read-only mapping over a private
          shallow copy. Its keys are fixed; its values are borrowed by identity and
          are NOT copied or frozen. Every bind receives a fresh dict of the
          entries, so a Spell clearing its own metadata never empties this one.
        - Metadata is immutable once created so decorated objects carry a
          stable registration contract: attributes cannot be set, added or
          deleted after construction.
        - `RESERVED_SPELL_METADATA_KEYS` names every argument the bind chain
          (`Spellbook.bind`, `Bind.bind`, `Bind._bind_logic`, `Spell.__init__`)
          takes natively, plus the three hook keys; `scan_bind` refuses them as
          metadata keys.

    Threading:
        Immutable once created; safe to share across threads. Values inside the
        application metadata are the caller's objects and keep whatever thread
        safety they have.

    Lifecycle / Cleanup:
        Owns no resources. Every reference it holds is borrowed from the
        decoration site and lives as long as the decorated object, so there is
        nothing to clean up. It is deliberately a slotted class rather than a
        dataclass: it holds callables, Protocol classes and arbitrary application
        values, and dataclasses here are reserved for plain values.

    Registration:
        MELDER KERNEL - guarded. Attached to decorated objects by
        `scan_bind(...)`.

    Subsystem Context:
        The frozen payload a `scan_bind` decoration leaves behind, consumed by
        `Scan` and replayed into `Spellbook.bind`.

    System Context:
        Preserving `Union[Existence, str]` and `Union[Permissions, str]` AS
        PROVIDED rather than normalizing at decoration time is the subtle
        correctness decision.
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
        Application metadata follows it at the outer level only: the mapping is
        read-only and copied out per bind, but its values are the caller's
        objects, exactly as a direct bind passes them through.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Frozen payload describing how a decorated object should be bound
        later. Melder kernel machinery: read it to understand the runtime, do not drive it
        directly.
    """
    __slots__ = (
        "existence",
        "permissions",
        "spellframe",
        "binding_name",
        "profile",
        "pre_hooks",
        "activation_hooks",
        "post_hooks",
        "resolvable",
        "disposal_method_names",
        "spell_metadata",
    )

    # Every name the bind chain takes natively. Metadata under one of these keys
    # would collide with (or shadow) a native argument somewhere between
    # `Spellbook.bind` and `Spell.__init__`, so `scan_bind` refuses it.
    RESERVED_SPELL_METADATA_KEYS: ClassVar[frozenset[str]] = frozenset({
        # Spellbook.bind, whose named parameters scan_bind mirrors.
        "self", "spell", "existence", "permissions", "spellframe", "binding_name",
        "disposal_method_names", "profile", "resolvable",
        # Construction hook keys Spellbook.bind takes from its keywords.
        "pre_hooks", "activation_hooks", "post_hooks",
        # Bind.bind and Bind._bind_logic.
        "aetheric_frame", "configured_disposal_method_names",
        "enforce_priority_disposal_methods", "_lifecycle_hooks",
        # Spell.__init__.
        "spell_index", "spell_name", "spell_type", "spell_id", "existing_object",
        "spellbook", "spellframe_kind", "implemented_protocols",
    })

    existence: Union[Existence, str]
    permissions: Union[Permissions, str]
    spellframe: Any
    binding_name: Optional[str]
    profile: str
    pre_hooks: Optional[tuple[Callable[..., Any], ...]]
    activation_hooks: Optional[tuple[Callable[..., Any], ...]]
    post_hooks: Optional[tuple[Callable[..., Any], ...]]
    resolvable: bool
    disposal_method_names: Optional[tuple[str, ...]]
    spell_metadata: Mapping[str, Any]

    def __init__(
            self,
            *,
            existence: Union[Existence, str],
            permissions: Union[Permissions, str],
            spellframe: Any,
            binding_name: Optional[str],
            profile: str,
            pre_hooks: Optional[tuple[Callable[..., Any], ...]],
            activation_hooks: Optional[tuple[Callable[..., Any], ...]],
            post_hooks: Optional[tuple[Callable[..., Any], ...]],
            resolvable: bool = True,
            disposal_method_names: Optional[tuple[str, ...]] = None,
            spell_metadata: Optional[Mapping[str, Any]] = None,
    ) -> None:
        """
        Store one declaration; `scan_bind`'s decorator calls this with normalized inputs.

        Contract:
            - Keyword-only, with the attribute names the former frozen dataclass
              used, so existing readers of the payload are unchanged.
            - Stores every value as given: `scan_bind` has already validated and
              normalized hooks, disposal names and metadata keys.
            - Copies `spell_metadata` into a private dict exposed only through a
              read-only mapping; None stores an empty mapping.
            - Writes through `object.__setattr__`, the only path past the
              immutability guard.

        Args:
            existence (Union[Existence, str]): Lifecycle scope, as declared.
            permissions (Union[Permissions, str]): Permissions, as declared.
            spellframe (Any): Spellframe or Protocol grouping key, or None.
            binding_name (Optional[str]): Binding name, or None.
            profile (str): Spell profile family to attach after bind.
            pre_hooks (Optional[tuple[Callable[..., Any], ...]]): Normalized hooks or None.
            activation_hooks (Optional[tuple[Callable[..., Any], ...]]): Normalized hooks or None.
            post_hooks (Optional[tuple[Callable[..., Any], ...]]): Normalized hooks or None.
            resolvable (bool): Native resolution capability, stored without coercion.
            disposal_method_names (Optional[tuple[str, ...]]): Normalized per-target
                disposal group, or None when none was declared.
            spell_metadata (Optional[Mapping[str, Any]]): Validated application
                metadata, or None for none.

        Returns:
            None.
        """
        object.__setattr__(self, "existence", existence)
        object.__setattr__(self, "permissions", permissions)
        object.__setattr__(self, "spellframe", spellframe)
        object.__setattr__(self, "binding_name", binding_name)
        object.__setattr__(self, "profile", profile)
        object.__setattr__(self, "pre_hooks", pre_hooks)
        object.__setattr__(self, "activation_hooks", activation_hooks)
        object.__setattr__(self, "post_hooks", post_hooks)
        object.__setattr__(self, "resolvable", resolvable)
        object.__setattr__(self, "disposal_method_names", disposal_method_names)
        object.__setattr__(
            self,
            "spell_metadata",
            MappingProxyType(dict(spell_metadata) if spell_metadata is not None else {}),
        )

    def __setattr__(self, name: str, value: Any) -> None:
        """
        Refuse every attribute write after construction.

        Args:
            name (str): Attribute the caller tried to set.
            value (Any): Ignored.

        Raises:
            AttributeError: Always; a declaration cannot change after decoration.
        """
        raise AttributeError(
            f"ScanBindMetadata is immutable; '{name}' cannot be set after decoration."
        )

    def __delattr__(self, name: str) -> None:
        """
        Refuse every attribute deletion.

        Args:
            name (str): Attribute the caller tried to delete.

        Raises:
            AttributeError: Always; a declaration cannot change after decoration.
        """
        raise AttributeError(
            f"ScanBindMetadata is immutable; '{name}' cannot be deleted."
        )

    def __repr__(self) -> str:
        """
        Describe the declaration for diagnostics.

        Contract:
            Shows the native options and the application-metadata KEYS only; the
            values are arbitrary application objects whose own repr is not run.

        Returns:
            str: A single-line description.
        """
        return (
            f"ScanBindMetadata(existence={self.existence!r}, "
            f"permissions={self.permissions!r}, spellframe={self.spellframe!r}, "
            f"binding_name={self.binding_name!r}, profile={self.profile!r}, "
            f"resolvable={self.resolvable!r}, "
            f"disposal_method_names={self.disposal_method_names!r}, "
            f"spell_metadata_keys={sorted(self.spell_metadata)!r})"
        )

    def to_bind_kwargs(self) -> dict[str, Any]:
        """
        Build the keyword payload consumed by `Spellbook.bind`.

        Purpose:
            Translate frozen scan metadata into the mutable hook/profile and
            application-metadata kwargs expected by the real binding pipeline.
        Contract:
            - Returns a dict containing only hook keys that were explicitly
              provided.
            - Hook tuples are copied into new lists so later bind-time mutation
              cannot alias back into stored metadata.
            - Always includes `profile`, because that value is part of the
              public scan-bind contract even when no hooks are supplied.
            - Includes every application-metadata entry in a dict that is new on
              every call; the values are the stored objects themselves. Metadata
              keys never collide with the hook or profile keys (they are
              reserved).
            - Leaves out the native policy arguments (existence, permissions,
              spellframe, binding_name, resolvable, disposal_method_names);
              `Scan.scan_module` passes those to `Spellbook.bind` explicitly.
        Returns:
            dict[str, Any]: Keyword arguments for Spellbook.bind hooks, profile and
            application metadata.
        """
        kwargs: dict[str, Any] = dict(self.spell_metadata)
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
        existence: Union[Existence, str],
        permissions: Union[Permissions, str],
        spellframe: Any = None,
        binding_name: Optional[str] = None,
        profile: str = "general",
        pre_hooks: Optional[Sequence[Callable[..., Any]]] = None,
        activation_hooks: Optional[Sequence[Callable[..., Any]]] = None,
        post_hooks: Optional[Sequence[Callable[..., Any]]] = None,
        resolvable: bool = True,
        disposal_method_names: Optional[Sequence[str]] = None,
        **spell_metadata: Any,
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
        - Accepts every option `Spellbook.bind` accepts for a target, with the
          same defaults: `resolvable`, per-target `disposal_method_names` and
          keyword application metadata. A scan replays them through
          `Spellbook.bind`, so a scanned registration matches a direct bind of
          the same target with the same options.
        - Intentional differences from direct binding: `permissions` is required
          here (direct bind defaults to "create"), and hook groups,
          disposal-name groups and metadata keys are checked now, at decoration,
          rather than when the module is scanned.
        - `resolvable` is stored exactly as given, with no truthiness coercion;
          Bind's strict bool check and its Protocol rules apply at scan time.
        - Disposal names and metadata are snapshotted: later changes to the
          caller's list or dict do not reach the declaration. Metadata values are
          kept by identity (a shallow copy), never copied or frozen.
        - Only the decorated object itself carries the declaration. Subclasses
          and instances of a decorated class are not scan targets unless they
          are decorated themselves.

    Args:
        existence (Union[Existence, str]):
            Explicit lifecycle scope for the spell (required).
        permissions (Union[Permissions, str]):
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
        resolvable (bool):
            Native per-version resolution capability, default True. False
            registers a non-resolvable definition, such as a Protocol that
            implementations are checked against. Forwarded unchanged to
            `Spellbook.bind`.
        disposal_method_names (Optional[Sequence[str]]):
            Ordered per-target disposal candidates, as a list or tuple of method
            names. At scan time they combine with the Book's configured
            candidates exactly as in `Spellbook.bind`; None and an empty group
            both leave the Book's candidates in force.
        **spell_metadata (Any):
            Application metadata for the registered Spell (`Spell.metadata`), as
            direct bind stores its extra keywords. Keys that the bind pipeline
            takes natively (`ScanBindMetadata.RESERVED_SPELL_METADATA_KEYS`) are
            refused.

    Returns:
        Callable[[Any], Any]: A decorator that tags the target object.

    Raises:
        ValueError: If `existence` or `permissions` is None.
        TypeError: If any hook list is not a list/tuple of callables, if
            `disposal_method_names` is not a list/tuple of strings, or if a
            metadata key is reserved.
    """
    if existence is None:
        raise ValueError("scan_bind requires an explicit existence value.")
    if permissions is None:
        raise ValueError("scan_bind requires an explicit permissions value.")

    pre_hooks_tuple = _normalize_hooks("pre_hooks", pre_hooks)
    activation_hooks_tuple = _normalize_hooks("activation_hooks", activation_hooks)
    post_hooks_tuple = _normalize_hooks("post_hooks", post_hooks)
    disposal_method_names_tuple = _normalize_disposal_method_names(disposal_method_names)
    spell_metadata_snapshot = _normalize_spell_metadata(spell_metadata)

    def decorator(obj: Any) -> Any:
        """
        Attach `ScanBindMetadata` to the decorated object.

        Contract:
            - Stores metadata under the reserved scan-bind attribute, in the
              object's own namespace - the only place a scan looks for it.
            - Each decorated object gets its own payload; one `scan_bind(...)`
              result applied to several objects shares no mutable state.
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
            resolvable=resolvable,
            disposal_method_names=disposal_method_names_tuple,
            spell_metadata=spell_metadata_snapshot,
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
        - Rejects re-exports: the object's `__module__` must match the module name.
        - Delegates all validation to `Spellbook.bind`.
        - Treats an object as a target only when its OWN namespace (`__dict__`)
          holds a scan-bind declaration; attributes seen through a base class,
          through an instance's class, through a metaclass or from `__getattr__`
          do not count.
        - Binds each object at most once per scan, however many module names
          refer to it; the first name in module order is the one reported.
        - Is not atomic: a failure part-way leaves the targets bound before it
          registered (see `Spellbook.scan`).

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
        OWN DECLARATION ONLY: `scan_bind` writes its payload into the decorated
        object's own namespace, and the scanner reads it from there and nowhere
        else. Reading it through `getattr` let an undecorated subclass, a
        module-level instance of a decorated class, a class whose metaclass was
        decorated, or a proxy answering every attribute look decorated, so a
        module's registrations depended on inheritance and attribute magic
        instead of on what its source declares.
        ONE BIND PER OBJECT PER SCAN closes the same hole for aliases: a module
        that keeps a second name for a decorated object would otherwise bind it
        twice and collide with itself. Identity decides, not equality; distinct
        objects that share a binding key still collide, and so does a rescan,
        because both are real duplicate registrations.
        Delegating ALL validation to `Spellbook.bind` means the deferred path
        and the direct path cannot diverge; there is one set of rules about what
        may become a spell, regardless of how it arrived.

    AGENT_ACCESS: public

    AGENT_PURPOSE:
        access: public. Deferred registration. Pass ONE module to Spellbook.scan(...) and it
        binds objects decorated with scan_bind. Module-only - no package traversal - and
        re-exports are rejected by __module__ check.
    """
    __slots__ = tuple(Cleanable.__slots__) + ("_spellbook",)

    def __init__(self, spellbook: "Spellbook") -> None:
        """
        Initialize a Scan helper bound to a specific Spellbook.

        Args:
            spellbook (Spellbook): The Spellbook used for binding.
        Raises:
            ValueError: If spellbook is None.

        Returns:
            None.
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

    @staticmethod
    def _own_scan_bind_metadata(candidate: Any) -> Any:
        """
        Return the scan-bind declaration an object carries in its own namespace.

        Purpose:
            Decide scan eligibility from the object's own declaration only.

        Contract:
            - Reads the object's own `__dict__` and returns the value stored under
              the scan-bind attribute, or None when there is none.
            - An object without a `__dict__`, or whose `__dict__` is not a dict or
              mappingproxy (for example a proxy that answers every attribute), has
              no declaration.
            - Never consults base classes, an instance's class, the metaclass or
              `__getattr__` for the declaration itself.
            - Returns the raw stored value; the caller checks its type.

        Args:
            candidate (Any): One value from the scanned module's namespace.

        Returns:
            Any: The stored value, or None when the object carries none.
        """
        # Module values are arbitrary external objects, so `__dict__` may be absent
        # or synthesized; anything that is not a real namespace has no declaration.
        namespace = getattr(candidate, "__dict__", None)
        if not isinstance(namespace, (dict, MappingProxyType)):
            return None
        return namespace.get(_SCAN_BIND_ATTR)

    def scan_module(self, module: ModuleType) -> list[str]:
        """
        Public API

        Scan a module for `scan_bind` metadata and bind all marked objects.

        Contract:
            - Walks the module dict in definition order.
            - A target is an object whose own `__dict__` holds the scan-bind
              declaration; every other value is skipped.
            - Each target is bound at most once per call, keyed by identity. The
              call holds a strong reference to every object it bound until it
              returns, so an id cannot be reused by a new object mid-scan.
            - Every target reaches `Spellbook.bind` with its declared existence,
              permissions, spellframe, binding_name, resolvable and
              disposal_method_names, plus `ScanBindMetadata.to_bind_kwargs()`
              (hook lists, profile and application metadata).
            - Not atomic: when a bind raises, the targets bound before it stay
              registered and the error propagates.

        Args:
            module (ModuleType): The module to scan for decorated targets.
        Returns:
            list[str]: Spell IDs bound during the scan, in module dict order.
        Raises:
            TypeError: If `module` is not a module or metadata is invalid, or as
                propagated from Spellbook.bind (for example a non-bool
                `resolvable` or a Protocol target left resolvable).
            ValueError: If a decorated object is not owned by the module, or as
                propagated from Spellbook.bind (lifetime rules).
            RuntimeError: Propagated from Spellbook.bind on binding errors.
        """
        self.check_cleaned()
        if not isinstance(module, ModuleType):
            raise TypeError("scan_module requires a Python module object.")

        module_name = module.__name__
        spell_ids: list[str] = []
        # Objects this scan bound, keyed by identity. Holding each object keeps its
        # id from being reused by a new object while the scan runs.
        bound_objects: dict[int, Any] = {}

        for attr_name, obj in vars(module).items():
            metadata = Scan._own_scan_bind_metadata(obj)
            if metadata is None:
                continue
            if not isinstance(metadata, ScanBindMetadata):
                raise TypeError(
                    f"scan_bind metadata for '{attr_name}' is invalid or corrupted."
                )
            if id(obj) in bound_objects:
                # Another module name for an object this scan already bound.
                continue

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
                resolvable=metadata.resolvable,
                disposal_method_names=metadata.disposal_method_names,
                **bind_kwargs,
            )
            bound_objects[id(obj)] = obj
            spell_ids.append(spell_id)

        return spell_ids


__all__ = ("scan_bind", "Scan", "ScanBindMetadata")
