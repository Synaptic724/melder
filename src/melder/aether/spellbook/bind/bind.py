import inspect
import threading
import hashlib
from typing import TYPE_CHECKING, Any, Callable, Optional, Sequence, Tuple, Union, ClassVar, TypeVar

if TYPE_CHECKING:
    from melder.aether.spellbook.spellbook import Spellbook
    from melder.aether.spellbook.spell_compiler.spell_examiner.profiles.binding_profile import (
        SpellBindingProfile,
    )



# Melder Imports
from melder.aether.spellbook.spell_types.spell_types import SpellType
from melder.aether.spellbook.existence.existence import Existence
from melder.utilities.general_base.cleanable import Cleanable
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.spellbook.spell import Spell
from melder._build_assets._bind_guard.bind_guard import INTERNAL_MANIFEST
from melder.utilities.custom_exceptions.internal_registration_error import InternalRegistrationError
from melder.utilities.custom_exceptions.hook_execution_error import HookExecutionError


BindHookSubject = TypeVar("BindHookSubject")
BindLifecycleHooks = tuple[
    tuple[Callable[[Any], object], ...],
    tuple[Callable[[Spell], object], ...],
    tuple[Callable[[Spell], object], ...],
]


def _internal_identity_of(candidate: Any) -> Tuple[str, str]:
    """
    Resolve the `(module, qualname)` identity used for manifest lookup.

    Contract:
        Classes answer for themselves; instances answer through `type(candidate)`,
        so binding an instance of an internal class is refused exactly like
        binding the class. Pure and deterministic - it reads two attributes and
        allocates nothing.

        `getattr` with a default is deliberate here and is NOT the defensive
        introspection the repo bans: `candidate` is arbitrary USER input whose
        attribute contract is not visible to us, which is the documented
        polymorphic/external exception. A target missing either attribute
        degrades to an empty string, which simply misses the manifest instead of
        raising - an unidentifiable object is not a melder internal.

    Args:
        candidate: The class or object being considered for registration.

    Returns:
        Tuple[str, str]: The candidate's module name and qualified name.
    """
    target_cls = candidate if isinstance(candidate, type) else type(candidate)
    module_name = getattr(target_cls, "__module__", "") or ""
    qualified_name = getattr(target_cls, "__qualname__", "") or ""
    return module_name, qualified_name


def assert_allowed(candidate: Any, context: str = "bind") -> None:
    """
    Refuse registration of a Melder-internal class as a spell.

    Purpose:
        The single enforcement seam for the internal-bind policy. `Bind` calls it
        once per registration; nothing else in the runtime consults the manifest.

    Contract:
        Membership is an EXACT `(module, qualname)` match against the generated
        `INTERNAL_MANIFEST` and does NOT walk the MRO. Listing `Cleanable` blocks
        `Cleanable` itself; a user subclass carries its own module and qualname,
        is absent from the manifest, and binds normally. That non-inheritance is
        precisely what allows the blanket "every class in the package is guarded"
        rule to exist without a curated exclusion list, and it is the accepted
        behaviour change from the retired `__melder_internal__` sentinel, which
        was read with `getattr` and therefore inherited.

        Guarding and exporting are ORTHOGONAL: this restricts REGISTRATION, never
        USE. Exported, user-constructible surfaces such as the custom exceptions
        and `ProtocolCrafter` stay importable and callable while being unbindable.

    Threading / Concurrency:
        Lock-free and safe under free-threaded 3.14t. `INTERNAL_MANIFEST` is an
        immutable module-level `frozenset`, so enforcement adds no contention to
        the bind path.

    Args:
        candidate: The class or object being offered for registration.
        context: Call-site label carried into the error message.

    Returns:
        None: Returns normally when the candidate is bindable.

    Raises:
        InternalRegistrationError: When the candidate's identity is present in
            the generated manifest.
    """
    module_name, qualified_name = _internal_identity_of(candidate)
    if (module_name, qualified_name) in INTERNAL_MANIFEST:
        raise InternalRegistrationError(
            f"Registration blocked for Melder internal object "
            f"(type={qualified_name}, module='{module_name}', context='{context}'). "
            f"Melder kernel/control-plane objects cannot be registered as spells."
        )

from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.spell_compiler.spell_examiner.spell_examiner import SpellExaminer
from melder.utilities.helpers.id_builder import IDBuilder
from melder.aether.spellbook.spell_compiler.spell_examiner.profiles.general_profile import (
    SpellGeneralProfile,
)
from melder.aether.spellbook.spell_compiler.spell_examiner.profiles.binding_profile import (
    ClassBindingProfile,
    CallableBindingProfile,
    InstanceBindingProfile,
    OtherBindingProfile,
)


#region Bind

class Bind(Cleanable):
    """
    Spellbook registration gateway for classes, callables, and concrete objects.

    `Bind` is the public control-plane surface that turns an arbitrary binding
    target into a canonical `Spell`. It is where lifecycle scope
    (`Existence`), access policy (`Permissions`), spellframe grouping, and
    structural fingerprinting first come together.

    The registration pipeline involves:
    1.  **Reflection:** Examining the object using `SpellExaminer` to create a binding profile.
    2.  **Fingerprinting:** Generating a deterministic SHA256 unique ID (`spell_id`) based on the profile.
    3.  **Validation:** Enforcing rules regarding naming conventions, existence, and spell type.
    4.  **Registration:** Creating the final `Spell` object, which encapsulates the component
        and its metadata for resolution and dependency injection.

    Contract:
    - `Bind` does not resolve spells; it registers them into one owning
      `Spellbook`.
    - Successful registration always flows through canonical profile
      examination and deterministic fingerprinting rather than ad hoc ids.
    - Decorator-style and direct-call usage share the same binding pipeline.
    - Resolution capability is native per-Spell policy, defaulting to True;
      disabling it does not change naming, lifetime, or ownership rules.
    - Classes and existing objects declared under a Protocol spellframe must
      satisfy its directly declared public members before Spell creation.
    - Owns the book's registration-hook sequences, distinct from application
      creation hooks. One immutable callback set is retained for each bind.
    - User callbacks execute synchronously outside the construction lock.
      Pre checks receive the input; activation receives the unpublished Spell.
      Spellbook signals post only after its registration work completes.

    Registration:
        MELDER KERNEL - guarded. Invoked through `Spellbook.bind(...)`; users
        call the spellbook, not this class.

    Subsystem Context:
        The registration gateway where lifecycle (`Existence`), access policy
        (`Permissions`), spellframe grouping, and structural fingerprinting
        first converge. It produces the `SpellIndex` + `Spell` pair the rest of
        the runtime resolves against.

    System Context:
        DETERMINISTIC FINGERPRINTING is the property everything downstream
        depends on. The `spell_id` is a SHA256 over the examined profile, so it
        is CONTENT-DERIVED and stable across processes and sessions - which is
        why the crystallizer can replay custody by recorded spell id while
        refusing to rehydrate ULIDs, and why the same object bound in two
        processes carries the same identity.
        The refusals are as load-bearing as the successes. Modules are rejected;
        Protocol targets require explicit `resolvable=False` because they have
        no construction contract. Method and lambda bindings are forced to `Existence.unique`
        because per-scope construction is meaningless for them. Rejecting at
        bind time is what keeps those errors adjacent to the mistake rather than
        surfacing deep inside a later meld.
        Bind is also a RECORDING moment: it is the structural emission point for
        the crystallizer, so custody is born here (gated on
        `activated AND dynamic posture`) rather than being swept up later.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Spellbook registration gateway for classes, callables, and concrete
        objects. Melder kernel machinery: read it to understand the runtime, do not drive it
        directly.
    """
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_spellbook",
        "_spell_examiner",
        "_lifecycle_hooks",
    ]
    _EMPTY_HOOKS: ClassVar[BindLifecycleHooks] = ((), (), ())
    _HOOK_NAMES: ClassVar[tuple[str, ...]] = ("bind:pre", "bind:activation", "bind:post")

    def __init__(
            self,
            spellbook: Spellbook,
            *,
            initial_hooks: Optional[BindLifecycleHooks] = None,
    ) -> None:
        """
        Initialize the spell registration gateway for one spellbook.

        Args:
            spellbook: Owning spellbook that will receive newly registered
                `Spell` instances.
            initial_hooks: Validated immutable configuration seed, or None for
                empty stages. Captured once; later changes stay Book-local.
        Contract:
            - Owns one `SpellExaminer` helper for profile creation.
            - Serializes registration work behind an internal lock.
            - Treats the supplied spellbook as the destination authority for
              all created spell bindings.
            - Owns callback tuple storage, but only borrows the callback objects;
              cleanup releases references without disposing user callbacks.

        Returns:
            None.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._spellbook: Spellbook = spellbook
        self._lock = threading.RLock()
        self._spell_examiner: SpellExaminer = SpellExaminer()
        self._lifecycle_hooks: BindLifecycleHooks = (
            self._EMPTY_HOOKS if initial_hooks is None else initial_hooks
        )

    def cleanup(self) -> None:
        """
        Cleans up resources held by the Bind instance.

        Bind itself does not own heavy resources beyond its lock, but we keep the
        cleanup pattern consistent with the rest of Melder. Once cleaned, the
        instance becomes inert and should not be reused.

        Contract:
        - Idempotent and lock-guarded.
        - Cleans the owned `SpellExaminer` before dropping references.
        - Releases stored callbacks without invoking their cleanup methods.
          An in-flight bind retains its own immutable callback set until it ends;
          callers must quiesce runtime work before destroying the owning book.
        - Leaves future callers to fail through `check_cleaned()`.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            if self._spell_examiner is not None:
                self._spell_examiner.cleanup()
            del self._spellbook
            del self._spell_examiner
            del self._lifecycle_hooks
        del self._lock

    def add_hooks(
            self,
            *,
            pre: Optional[Sequence[Callable[[Any], object]]] = None,
            activation: Optional[Sequence[Callable[[Spell], object]]] = None,
            post: Optional[Sequence[Callable[[Spell], object]]] = None,
    ) -> None:
        """
        Append validated registration callbacks for this book's future binds.

        Contract:
            Validates all supplied stages before changing any. Preserves order
            and repeated registrations; None or an empty sequence adds nothing.
            Replaces the immutable registry under the Bind lock, then asks the
            owning Book to refresh its recording markers before releasing it.
            The Book emission seam takes no Book registry lock.

        Args:
            pre: Synchronous reference checks; reject by raising.
            activation: Callbacks receiving the newly constructed Spell.
            post: Callbacks receiving the completed active or parked binding.

        Returns:
            None. Callback return values do not replace the binding target.

        Raises:
            TypeError: If a supplied item is not callable.
            RuntimeError: If this Bind has been cleaned.
        """
        self.check_cleaned()
        additions: BindLifecycleHooks = (
            () if pre is None else tuple(pre),
            () if activation is None else tuple(activation),
            () if post is None else tuple(post),
        )
        for stage_name, callbacks in zip(self._HOOK_NAMES, additions):
            for callback in callbacks:
                if not callable(callback):
                    raise TypeError(f"{stage_name} hooks must contain only callable objects.")
        if not any(additions):
            return
        with self._lock:
            self.check_cleaned()
            self._lifecycle_hooks = (
                self._lifecycle_hooks[0] + additions[0],
                self._lifecycle_hooks[1] + additions[1],
                self._lifecycle_hooks[2] + additions[2],
            )
            self._spellbook._emit_bind_hook_presence()

    def clear_hooks(self) -> None:
        """
        Release all registered bind callbacks and refresh recorded presence.

        Contract:
            Serializes replacement and emission with registration. Already-running
            binds keep their captured tuple; later binds use the empty registry.
            Does not clean user callback objects. Clearing an empty registry is
            a no-op, including for the recording journal.

        Returns:
            None.

        Raises:
            RuntimeError: If this Bind has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            self.check_cleaned()
            if not any(self._lifecycle_hooks):
                return
            self._lifecycle_hooks = self._EMPTY_HOOKS
            self._spellbook._emit_bind_hook_presence()

    def capture_hooks(self) -> BindLifecycleHooks:
        """
        Retain one immutable callback set for a complete binding operation.

        Contract:
            Returns the current tuple reference without copying its contents.
            Atomic tuple replacement keeps all three stages from one registration
            state, even if callbacks or other threads add/clear hooks mid-bind.
            This retention is required for operation consistency, not a defensive
            copy of an owned mutable registry.

        Returns:
            BindLifecycleHooks: Ordered pre, activation and post tuples.

        Raises:
            RuntimeError: If this Bind has been cleaned.
        """
        self.check_cleaned()
        return self._lifecycle_hooks

    def get_hook_names(self) -> tuple[str, ...]:
        """
        Describe nonempty registration stages using value-only record markers.

        Returns:
            tuple[str, ...]: Stage names in pre/activation/post order. Callback
            functions and their identities never enter the persistence payload.

        Raises:
            RuntimeError: If this Bind has been cleaned.
        """
        return tuple(
            name for name, callbacks in zip(self._HOOK_NAMES, self.capture_hooks()) if callbacks
        )

    @staticmethod
    def execute_post_hooks(spell: Spell, hooks: BindLifecycleHooks) -> None:
        """
        Notify the captured post stage after Book registration has completed.

        Args:
            spell: The actual active or parked Spell after normal publication.
            hooks: The callback set retained at this bind's entry.

        Contract:
            Runs outside Bind's construction lock. This is a registration
            notification, not an outer-transaction commit notification; failures
            do not undo published state or arbitrary external callback effects.

        Returns:
            None.

        Raises:
            HookExecutionError: A callback failed; later callbacks are skipped.
        """
        if hooks[2]:
            Bind._execute_bind_hooks(hooks[2], spell, "post_bind")

    @staticmethod
    def _execute_bind_hooks(
            hooks: Sequence[Callable[[BindHookSubject], object]],
            subject: BindHookSubject,
            phase: str,
    ) -> None:
        """
        Invoke one ordered synchronous stage with its unchanged subject.

        Args:
            hooks: Captured callbacks for this stage.
            subject: Original reference or actual Spell, according to the stage.
            phase: Stable phase name used by HookExecutionError.

        Returns:
            None. Return values are ignored; a check rejects by raising.

        Raises:
            HookExecutionError: Wraps and chains the first ordinary callback
                exception, preserving its name and phase. Later callbacks stop.
        """
        for hook in hooks:
            try:
                hook(subject)
            except Exception as error:
                # Callbacks are external callables; __name__ is not contractual.
                hook_name = getattr(hook, "__name__", repr(hook))
                raise HookExecutionError(phase, hook_name, error) from error

    @staticmethod
    def _cleanup_unpublished_spell(spell: Spell, spell_index: SpellIndex) -> None:
        """
        Retire a newly constructed Spell after failure before publication.

        Args:
            spell: Unpublished allocation owned by the failing bind operation.
            spell_index: Its newly allocated index, never an existing target index.

        Contract:
            Selects the existing local Spell teardown path; public Book removal
            requires a registered Spell and must not run here. Cleans the owned
            index even if Spell cleanup fails. Supplied application objects are
            references only and are never disposed by this teardown.

        Returns:
            None.
        """
        spell._spellbook_cleanup = True
        try:
            spell.cleanup()
        finally:
            spell_index.cleanup()

    def bind(
            self,
            permissions: Permissions,
            existence: Existence,
            *,
            aetheric_frame: str,
            spell: Any = None,
            spellframe: Any = None,
            binding_name: Optional[str] = None,
            configured_disposal_method_names: Optional[Sequence[str]] = None,
            profile: str = "general",
            disposal_method_names: Optional[Sequence[str]] = None,
            enforce_priority_disposal_methods: bool = False,
            resolvable: bool = True,
            _lifecycle_hooks: Optional[BindLifecycleHooks] = None,
            **kwargs: Any,
    ) -> Union[Spell, Any]:
        """
        Register a class, function, or existing object as a `Spell`.

        This method supports two usage patterns:
        1. **Direct Call:** `bind(permissions, spell=MyClass, ...)`
        2. **Decorator:** `@Bind.bind(permissions, ...)` applied to a class or function.

        In both modes, the same binding pipeline is used: examine the target,
        fingerprint the binding profile, validate spellframe / existence rules,
        and register the canonical `Spell` into the owning spellbook.

        Args:
            permissions (Permissions): The access level for this spell (e.g., read, create, block).
            aetheric_frame (str): The Aetheric Frame (logical container) this spell belongs to.
            spell (Any, optional): The class, function, or existing object to bind. Required for direct usage.
            spellframe (Optional[Any]): Logical interface or Protocol used as the DI contract / grouping key.
            binding_name (Optional[str]): A specific key used to distinguish this spell among others in its frame.
            profile (str): Spell profile family to attach to the final Spell.
            existence (Existence): The lifecycle scope for this spell (default is `Existence.unique`).
            configured_disposal_method_names (Optional[Sequence[str]]): Ordered book-level disposal candidates.
            disposal_method_names (Optional[Sequence[str]]): Ordered candidates specific to this binding.
            enforce_priority_disposal_methods (bool): Place the matching book block first when
                True, last when False (default). Book order owns shared names in both modes.
            resolvable (bool): Native resolution capability for this Spell version.
                False permits descriptive Protocol targets; it does not relax other binding rules.
            _lifecycle_hooks: Internal Book-captured callback set, retained through
                its later post stage. None captures the current registry when the
                actual target is supplied, including deferred decorator calls.
        Contract:
            - When `spell` is omitted, returns a decorator that will bind the
              later target with the supplied policy and lifecycle settings.
            - When `spell` is supplied directly, runs the full binding pipeline
              immediately and returns the created `Spell`.
            - Decorator and direct-call modes are semantically equivalent once
              the target object is known.
            - A Protocol spellframe checks directly declared public members on
              a class or supplied existing object. Callable bindings retain
              their separate factory/handler contract.
            - Matching book names form one ordered block, including names also supplied
              explicitly. Spell-only names keep their order before or after that block.
              Each matching name is retained once.
              An empty spell-specific group does not disable configured book candidates.

        Returns:
            Union[Spell, Any]:
                - If used without a target, returns a decorator that produces a Spell.
                - If used as a direct call, returns the newly created `Spell` instance.

        Raises:
            TypeError: If a class or supplied existing object lacks a required
                directly declared Protocol member or exposes a non-callable
                value where that Protocol requires a callable, or resolvable is not a bool.
        """
        self.check_cleaned()
        if spell is None:
            # Decorator usage
            def decorator(obj: Any) -> Spell:
                """
                Bind the target object with the specified policy and lifecycle settings.
                """

                return self._bind_logic(
                    obj,
                    spellframe,
                    binding_name,
                    existence,
                    permissions,
                    aetheric_frame,
                    configured_disposal_method_names,
                    profile,
                    disposal_method_names=disposal_method_names,
                    enforce_priority_disposal_methods=enforce_priority_disposal_methods,
                    resolvable=resolvable,
                    _lifecycle_hooks=_lifecycle_hooks,
                    **kwargs,
                )

            return decorator
        else:
            # Direct usage
            return self._bind_logic(
                spell,
                spellframe,
                binding_name,
                existence,
                permissions,
                aetheric_frame,
                configured_disposal_method_names,
                profile,
                disposal_method_names=disposal_method_names,
                enforce_priority_disposal_methods=enforce_priority_disposal_methods,
                resolvable=resolvable,
                _lifecycle_hooks=_lifecycle_hooks,
                **kwargs,
            )

    def _bind_logic(
            self,
            spell: Any,
            spellframe: Optional[Any],
            binding_name: Optional[str],
            existence: Existence,
            permissions: Permissions,
            aetheric_frame: str,
            configured_disposal_method_names: Optional[Sequence[str]] = None,
            profile: str = "general",
            disposal_method_names: Optional[Sequence[str]] = None,
            enforce_priority_disposal_methods: bool = False,
            resolvable: bool = True,
            _lifecycle_hooks: Optional[BindLifecycleHooks] = None,
            **kwargs: Any,
    ) -> Spell:
        """
        Internal logic for processing the binding of a spell object.

        This method performs the full binding pipeline:
        * Validates existence and method/lambda constraints.
        * Enforces Protocol/Spellframe semantics:
          - Protocol targets require explicit resolvable=False.
          - Class-based and existing-object spells bound under a Protocol
            spellframe must satisfy its directly declared public members.
            Existing objects are checked on the supplied value, not its class.
          - Method/lambda spells may also be grouped under Protocol or string
            spellframes (factory / handler semantics), but are not structurally
            validated against the Protocol.
        * Computes a deterministic fingerprint and SpellIndex from a `SpellBindingProfile`.
        * Resolves disposal names once in group priority order, hashes the resolved
          list, and passes that same list to Spell without another conversion.
        * Determines the canonical SpellType.
        * Constructs the final `Spell` instance.
        * Replaces the initial raw binding artifact with the combined
          spell-facing general profile once the `Spell` exists.

        Args:
            spell (Any): The class, function, or existing object to bind.
            spellframe (Optional[Any]): Logical interface or category for grouping
                (typically a Protocol used as a DI contract).
            binding_name (Optional[str]): A specific key used to distinguish this spell.
            profile (str): Spell profile family to attach after Spell creation.
            existence (Existence): The lifecycle scope for this spell.
            permissions (Permissions): The access level for this spell.
            aetheric_frame (str): The Aetheric Frame this spell belongs to.
            configured_disposal_method_names (Optional[Sequence[str]]): Ordered book candidates.
            disposal_method_names (Optional[Sequence[str]]): Ordered per-spell candidates.
            enforce_priority_disposal_methods (bool): Book block first when True, last otherwise.
            resolvable (bool): Immutable resolution capability, validated before target reflection.
            _lifecycle_hooks: Optional callback set captured by Book for this operation.

        Hook contract:
            Pre receives the original reference before reflection. Activation
            receives the actual Spell immediately after construction and before
            profile completion. Both run outside the construction lock. Activation
            or profile failure retires the unpublished Spell and its fresh index.
            Native fingerprint rules are unchanged and callback returns are ignored.

        Disposal contract:
            Retain declared profile methods and requested inherited callables,
            respecting the first class declaration in Python's MRO. Non-callable
            shadows and hidden dunders remain excluded; descriptors are not invoked
            during matching. The shallow profile and its fingerprint inputs do not
            expand. Missing names and non-class profiles contribute nothing. Book names
            own overlaps in both modes and keep their configured order. Spell-only
            names keep their supplied order, before or after the book block. Each
            matching name appears once in the single result list.
            The result is established before identity and registration; no method
            lookup, invocation, or policy recheck is added to the resolution path.

        Returns:
            Spell: The newly created and configured Spell instance.

        Raises:
            TypeError:
                - If resolvable is not a bool, or a Protocol target is resolvable.
                - If a class or existing object under a Protocol spellframe
                  fails its directly declared public-member check.
            ValueError:
                - If the binding is otherwise invalid (existence errors, lambda
                  without name, etc.).
            HookExecutionError: A pre-bind or bind-activation callback failed.
        """
        hooks = self.capture_hooks() if _lifecycle_hooks is None else _lifecycle_hooks
        if hooks[0]:
            self._execute_bind_hooks(hooks[0], spell, "pre_bind")
        with self._lock:
            self.check_cleaned()
            Bind._validate_resolvable(resolvable)
            # 0. Block registration of Melder internal objects/classes.
            assert_allowed(spell, context="bind")
            # 0.1 Reject modules outright.
            if inspect.ismodule(spell):
                raise TypeError(
                    f"Cannot bind module '{spell.__name__}'. Provide a class/function/object instead."
                )

            # ------------------------------------------------------------------
            # 1. Reject Protocols as resolvable spells
            # ------------------------------------------------------------------
            # Protocols define *interfaces*, not constructible implementations.
            # A Protocol may be a spellframe or an explicitly non-resolvable
            # definition; it cannot be a concrete provider.
            if resolvable and Bind._is_protocol_type(spell):
                raise TypeError(
                    f"Cannot bind Protocol '{spell.__name__}' as a concrete spell. "
                    f"Use it as a spellframe (DI contract), or pass resolvable=False "
                    f"to register a non-resolvable definition."
                )

            # ------------------------------------------------------------------
            # 2. Build binding profile and fingerprint
            # ------------------------------------------------------------------
            provisional_general_profile = self._spell_examiner.create_profile(
                spell,
                profile,
            )
            if not isinstance(provisional_general_profile, SpellGeneralProfile):
                raise TypeError(
                    "General profile creation must return SpellGeneralProfile."
                )
            binding_profile: SpellBindingProfile = provisional_general_profile.binding_profile
            spell_name = getattr(spell, "__name__", type(spell).__name__)
            resolved_disposal_method_names: list[str] = []
            if isinstance(binding_profile, ClassBindingProfile):
                # Establish book ownership of overlaps before placing spell-only names.
                if configured_disposal_method_names is not None:
                    for method_name in configured_disposal_method_names:
                        if (
                                Bind._matches_disposal_method(binding_profile, method_name)
                                and method_name not in resolved_disposal_method_names
                        ):
                            resolved_disposal_method_names.append(method_name)
                spell_position = len(resolved_disposal_method_names) if enforce_priority_disposal_methods else 0
                if disposal_method_names is not None:
                    for method_name in disposal_method_names:
                        if (
                                Bind._matches_disposal_method(binding_profile, method_name)
                                and method_name not in resolved_disposal_method_names
                        ):
                            resolved_disposal_method_names.insert(spell_position, method_name)
                            spell_position += 1
            fingerprint: str = Bind.sha256_profile(
                binding_profile,
                spellframe=spellframe,
                spell_name=spell_name,
                binding_name=binding_name,
                existence=existence,
                disposal_method_names=resolved_disposal_method_names,
                resolvable=resolvable,
            )
            spell_index = SpellIndex(initial_id=fingerprint)

            # Check if this should be treated as an "existing creation"
            is_instance = isinstance(
                binding_profile, (InstanceBindingProfile, OtherBindingProfile)
            )

            # ------------------------------------------------------------------
            # 3. Generic binding validation (existence + callable rules)
            # ------------------------------------------------------------------
            Bind._validate_binding(binding_profile, binding_name, existence)

            # ------------------------------------------------------------------
            # 4. Protocol spellframe semantics
            # ------------------------------------------------------------------
            # If the caller provided a Protocol as the spellframe:
            #   * For classes and existing objects: check the actual target's
            #     members, including instance-only or shadowed implementations.
            #   * For callable spells: allow binding (factory/handler semantics),
            #     but do not run structural checks (no meaningful attribute set).
            if spellframe is not None and Bind._is_protocol_type(spellframe):
                if isinstance(binding_profile, ClassBindingProfile) or is_instance:
                    ok, missing_members = Bind._structurally_implements_protocol(
                        spell, spellframe
                    )
                    if not ok:
                        missing_str = ", ".join(sorted(missing_members))
                        target_kind = "Existing object" if is_instance else "Class"
                        raise TypeError(
                            f"{target_kind} '{spell_name}' does not structurally implement "
                            f"Protocol '{spellframe.__name__}'. "
                            f"Missing members: {missing_str}"
                        )
                # For CallableBindingProfile (functions/lambdas), we accept the
                # Protocol spellframe as a callable contract / grouping key without
                # structural validation at this stage.

            # ------------------------------------------------------------------
            # 5. Determine the spell type (enum classification)
            # ------------------------------------------------------------------
            spell_type = Bind._determine_spell_type(
                binding_profile=binding_profile,
                name=binding_name,
                spellframe=spellframe,
            )

            # ------------------------------------------------------------------
            # 6. Construct the Spell object
            # ------------------------------------------------------------------
            new_spell = Spell(
                spell=spell,
                spell_index=spell_index,
                spellframe=spellframe,
                binding_name=binding_name,
                spell_name=str(spell_name),
                existence=existence,
                spell_type=spell_type,
                profile=provisional_general_profile,
                spell_id=fingerprint,
                permissions=permissions,
                aetheric_frame=aetheric_frame,
                existing_object=spell if is_instance else None,
                spellbook=self._spellbook,
                disposal_method_names=resolved_disposal_method_names,
                resolvable=resolvable,
                # Owner ruling 2026-07-19: leftover bind kwargs flow into
                # Spell's OWN kwargs channel (Spell.__init__ stores them as
                # spell.metadata). Native params stay sovereign: a colliding
                # key fails loudly from Spell's signature.
                **kwargs,
            )

        # User callbacks may register hooks or bind recursively; do not hold the
        # construction lock while calling them. The captured tuples stay stable.
        completed = False
        try:
            if hooks[1]:
                self._execute_bind_hooks(hooks[1], new_spell, "bind_activation")
            provisional_general_profile.complete_with_spell(new_spell)
            completed = True
            return new_spell
        finally:
            if not completed:
                self._cleanup_unpublished_spell(new_spell, spell_index)

    @staticmethod
    def _matches_disposal_method(profile: ClassBindingProfile, method_name: str) -> bool:
        """
        Match one disposal candidate without expanding the class binding profile.

        Contract:
            Preserve existing declared-method eligibility. For other non-dunder
            names, inspect class namespaces in MRO order and stop at the first
            declaration, including a non-callable shadow. A local declaration
            excluded by the profile stays excluded. Raw inherited members use
            the same callable test as the profile builder; properties and raw
            classmethod descriptors remain unsupported. Never invoke descriptors
            or admit metaclass-only members as instance disposal methods.

        Args:
            profile: Binding-time profile of the registered class.
            method_name: Requested configured or per-spell disposal name.

        Returns:
            bool: Whether the class exposes an eligible disposal candidate.

        Lifecycle / Threading:
            Runs under the existing Bind lock before fingerprinting. Owns no
            state, invokes no cleanup and adds no work to ordinary resolution.
        """
        if method_name in profile.method_names:
            return True
        if method_name.startswith("__") and method_name.endswith("__"):
            return False
        for owner in profile.original_object.__mro__:
            if method_name in owner.__dict__:
                return owner is not profile.original_object and callable(owner.__dict__[method_name])
        return False

    #region Spell Inspector Helpers
    @staticmethod
    def spell_id_inspector(
            spell: Any,
            *,
            spellframe: Any = None,
            spell_name: Optional[str] = None,
            binding_name: Optional[str] = None,
            existence: Existence = Existence.unique,
            disposal_method_names: Sequence[str] = (),
            resolvable: bool = True,
    ) -> str:
        """
        Compute the canonical spell fingerprint without registering the spell.

        This is the read-only convenience path for tooling or diagnostics that
        need the same deterministic fingerprint used by the real binding
        pipeline but do not want to create or register a `Spell`.

        Args:
            spell (Any): The spell object (class, function, or instance) to inspect.
            spellframe (Optional[Any]): Logical interface or Protocol used as the DI contract / grouping key.
            spell_name (Optional[str]): A specific key used to distinguish this spell among others in its frame.
            binding_name (Optional[str]): A specific key used to distinguish this spell.
            existence (Existence): The lifecycle scope for this spell.
            disposal_method_names (Sequence[str]): Already-resolved disposal names in execution order.
            resolvable (bool): Per-version capability; omission preserves the legacy fingerprint.
        Contract:
            - Builds the same `SpellGeneralProfile` / `SpellBindingProfile`
              chain used by the real binding path.
            - Returns the same fingerprint that `_bind_logic(...)` would use
              when supplied the same resolved name, binding metadata, and ordered
              disposal list. This helper does not apply book priority or match names.
            - Does not register anything into a spellbook or mutate runtime
              binding state.

        Returns:
            str: A unique identifier string (SHA256 hash) for the spell.

        Raises:
            TypeError: If resolvable is not a bool; checked before target reflection.
        """
        Bind._validate_resolvable(resolvable)
        profile = SpellGeneralProfile.create_from_target(spell)
        return Bind.sha256_profile(
            profile.binding_profile,
            spellframe=spellframe,
            spell_name=spell_name,
            binding_name=binding_name,
            existence=existence,
            disposal_method_names=tuple(disposal_method_names),
            resolvable=resolvable,
        )

    @staticmethod
    def sha256_profile(
            profile: SpellBindingProfile,
            *,
            spellframe: Any = None,
            spell_name: Optional[str] = None,
            binding_name: Optional[str] = None,
            existence: Optional[Existence] = None,
            disposal_method_names: Sequence[str] = (),
            resolvable: bool = True,
    ) -> str:
        """
        Computes the SHA256 hash of a spell's binding profile metadata.

        The binding profile includes just enough structural metadata to create a
        unique, versioned fingerprint of the spell's shape.

        This function is intentionally coupled to the `SpellBindingProfile`
        dataclasses rather than the heavier inspector profiles.

        Contract:
            - Fingerprints normalized bind-time metadata only, not transient
              runtime object identity.
            - Uses the explicit `v4-binding` schema prefix for omitted/True and
              `v4-binding-non-resolvable` for False, preserving all remaining inputs so future
              fingerprint-shape changes can version cleanly. v4 replaced the
              class source preview (first-5-lines text: docstring-sensitive,
              constructor-blind, and the only source-file read on the bind
              hot path) with the constructor signature string, so the
              fingerprint tracks exactly the shape compiled wiring depends
              on: constructor changes invalidate caches, docstring edits do
              not.
            - Includes the direct bind-time parameters that shape later
              compiler/runtime behavior: spell_name, spellframe, binding_name,
              existence, resolvable, and resolved disposal metadata in execution order.
            - Equal bind signatures produce equal hashes; materially different
              signatures should produce different hashes.
        Returns:
            str: Deterministic SHA256 fingerprint for the supplied binding
                profile.

        Raises:
            TypeError: If resolvable is not a bool; no truthiness coercion is applied.
        """
        Bind._validate_resolvable(resolvable)
        # Keep the legacy schema intact; only False selects a different hash domain.
        parts: list[str] = ["v4-binding" if resolvable else "v4-binding-non-resolvable"]

        if isinstance(profile, ClassBindingProfile):
            parts += [
                profile.name,
                profile.qualname,
                profile.module,
                ",".join(sorted(profile.bases)),
                ",".join(sorted(profile.mro)),
                ",".join(sorted(profile.annotations.keys())),
                ",".join(sorted(profile.method_names)),
                profile.init_signature or "",
            ]
        elif isinstance(profile, CallableBindingProfile):
            param_parts = [
                f"{p.name}:{p.kind}={p.default_repr}"
                for p in (profile.parameters or ())
            ]
            parts += [
                profile.name,
                profile.qualname or "",
                profile.module or "",
                profile.signature or "",
                ",".join(param_parts),
                (profile.repr_string or "").strip(),
                profile.type_name,
                "lambda" if profile.lambda_function else "",
                "builtin" if profile.builtin_module else "",
                "extension" if profile.extension_module else "",
                ]
        elif isinstance(profile, InstanceBindingProfile):
            parts += [
                profile.type_name,
                profile.module or "",
                (profile.repr_string or "").strip(),
                ]
        elif isinstance(profile, OtherBindingProfile):
            parts += [
                profile.type_name,
                profile.module or "",
                (profile.repr_string or "").strip(),
                ]
        else:
            # Absolute fallback – should effectively never happen.
            parts.append(repr(type(profile)))

        if spell_name is not None:
            parts.append(spell_name)
        if spellframe is not None:
            parts.append(str(spellframe))
        if binding_name is not None:
            parts.append(binding_name)

        if existence is not None:
            parts.append(existence.name)

        parts.extend(tuple(disposal_method_names))

        key = "::".join(parts)
        return hashlib.sha256(key.encode("utf-8")).hexdigest()

    @staticmethod
    def _validate_resolvable(resolvable: bool) -> None:
        """
        Reject non-boolean capability inputs at independent admission/fingerprint boundaries.

        Args:
            resolvable: Per-version resolution capability supplied by the caller.

        Returns:
            None. Accepts True and False without conversion or state changes.

        Raises:
            TypeError: If a number, string, None or other non-bool value is supplied.
        """
        if type(resolvable) is not bool:
            raise TypeError(
                f"resolvable must be a bool (True or False), got {type(resolvable).__name__}. "
                "Pass resolvable=False to register a non-resolvable definition."
            )

    @staticmethod
    def _validate_binding(
            profile: SpellBindingProfile,
            binding_name: Optional[str],
            existence: Existence,
    ) -> None:
        """
        Enforce binding-policy rules before a `Spell` is created.

        This is the policy gate that keeps obviously-invalid bindings out of
        the spellbook before profile fingerprinting and spell construction are
        allowed to proceed.

        Args:
            profile (SpellBindingProfile): The binding profile of the spell.
            binding_name (Optional[str]): The optional binding name provided.
            existence (Existence): The lifecycle scope provided.
        Contract:
            - Rejects invalid `Existence` values up front.
            - Forces pre-created object bindings into `Existence.unique`
              because they are already materialized and cannot participate in
              the other factory-driven lifecycle modes.
            - Enforces lambda naming and callable lifecycle restrictions before
              registration.

        Raises:
            ValueError: If the binding violates any rule:
                - Lambda/method bound without a required binding name.
                - Method/lambda spells bound with an existence type other than `Existence.unique`.
                - Existing-object spells bound with an existence type other than `Existence.unique`.
                - Invalid `existence` type provided.
        """
        # Validate that existence is a valid Existence member.
        Bind._existence_check(existence)

        # ------------------------------------------------------------------
        # Existing-object spells: must be Existence.unique (global singleton)
        # ------------------------------------------------------------------
        #
        # Existing creations are pre-instantiated and cannot participate in any
        # other lifecycle – they are always treated as singletons for the entire
        # Aetheric Frame. If the caller tries to bind an existing object with
        # any other existence type, we fail fast.
        #
        if isinstance(profile, (InstanceBindingProfile, OtherBindingProfile)) and existence is not Existence.unique:
            raise ValueError(
                "Existing-object spells must use Existence.unique. "
                "Pre-created instances are always treated as singletons and "
                "cannot be bound with other lifecycle modes."
            )

        # NOTE:
        # -----
        # We now ALLOW binding names for existing instances.
        # Existing-object spells are treated as opaque, non-recreatable creations.
        # They can be named and participate in spellframes, but do not act as factories.

        # ------------------------------------------------------------------
        # Lambda / method rules
        # ------------------------------------------------------------------
        if isinstance(profile, CallableBindingProfile):
            # Enforce lambda naming rule
            if profile.lambda_function and not binding_name:
                raise ValueError(
                    "Cannot bind a lambda method without providing a `name=`. "
                    "Lambdas must be registered as LAMBDA_METHOD_WITH_BINDING_NAME spells."
                )

            # Methods / lambdas are forced to unique existence
            if existence is not Existence.unique:
                raise ValueError("Method and lambda spells must use Existence.unique.")

    @staticmethod
    def _existence_check(existence: Existence) -> bool:
        """
        Assert that the supplied lifecycle mode is a real `Existence` member.

        Args:
            existence (Existence): The object to check.
        Contract:
            - Accepts only concrete `Existence` enum members.
            - Raises immediately instead of silently coercing or defaulting.

        Returns:
            bool: True if the object is a valid `Existence` instance.

        Raises:
            ValueError: If the object is not an instance of `Existence`.
        """
        if not isinstance(existence, Existence):
            raise ValueError(
                f"Invalid existence type: {existence}. Must be an instance of Existence."
            )
        return True

    @staticmethod
    def _determine_spell_type(
            binding_profile: SpellBindingProfile,
            name: Optional[str],
            spellframe: Optional[Any],
    ) -> SpellType:
        """
        Determines the canonical `SpellType` based on the spell's binding profile
        and binding metadata.

        This helps the system categorize the spell for later resolution
        (e.g., class, method, named, spellframe-scoped, existing creation).

        Args:
            binding_profile (SpellBindingProfile): The binding profile of the spell.
            name (Optional[str]): The optional binding name provided.
            spellframe (Optional[Any]): The optional spell frame / protocol provided.

        Returns:
            SpellType: The determined type of the spell.
        """

        # -------------------------------------------------------
        # CLASS-BASED SPELLS
        # -------------------------------------------------------
        if isinstance(binding_profile, ClassBindingProfile):
            if name and spellframe:
                return SpellType.SPELL_WITH_BINDING_NAME_WITH_SPELLFRAME
            if spellframe:
                return SpellType.SPELL_WITH_SPELLFRAME
            if name:
                return SpellType.SPELL_WITH_BINDING_NAME
            return SpellType.SPELL

        # -------------------------------------------------------
        # METHOD / FUNCTION / LAMBDA SPELLS
        # -------------------------------------------------------
        if isinstance(binding_profile, CallableBindingProfile):
            # Lambdas always require a binding name and get their own type family.
            if binding_profile.lambda_function:
                if name and spellframe:
                    return SpellType.LAMBDA_METHOD_WITH_BINDING_NAME_WITH_SPELLFRAME
                if spellframe and not name:
                    return SpellType.LAMBDA_METHOD_WITH_SPELLFRAME
                return SpellType.LAMBDA_METHOD_WITH_BINDING_NAME

            # Non-lambda methods / functions
            if name and spellframe:
                return SpellType.METHOD_WITH_BINDING_NAME_WITH_SPELLFRAME
            if spellframe:
                return SpellType.METHOD_WITH_SPELLFRAME
            if name:
                return SpellType.METHOD_WITH_BINDING_NAME
            return SpellType.METHOD

        # -------------------------------------------------------
        # EXISTING OBJECT / OTHER SPELLS
        # -------------------------------------------------------
        if isinstance(binding_profile, (InstanceBindingProfile, OtherBindingProfile)):
            if name and spellframe:
                return SpellType.EXISTING_CREATION_WITH_BINDING_NAME_WITH_SPELLFRAME
            if spellframe:
                return SpellType.EXISTING_CREATION_WITH_SPELLFRAME
            return SpellType.EXISTING_CREATION

        # -------------------------------------------------------
        # FALLBACK (should almost never happen, but be safe)
        # -------------------------------------------------------
        return SpellType.EXISTING_CREATION

    # ------------------------------------------------------------------
    # Protocol helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _is_protocol_type(obj: Any) -> bool:
        """
        Returns True if `obj` is a `typing.Protocol`-style interface.

        Instead of using ``issubclass(obj, Protocol)`` (which static type
        checkers complain about unless the protocol is marked
        ``@runtime_checkable``), we rely on the internal flag that
        ``typing.Protocol`` sets on all protocol subclasses.

        This keeps the check runtime-friendly and IDE-friendly while still
        correctly identifying Protocol-based spellframes.
        """
        if not inspect.isclass(obj):
            return False

        # PEP 544 / typing implementation detail:
        # Protocol subclasses have a private flag set on the class.
        # Different Python versions may use `_is_protocol` or `__is_protocol__`,
        # so we check both defensively.
        if getattr(obj, "_is_protocol", False):
            return True
        if getattr(obj, "__is_protocol__", False):
            return True

        return False

    @staticmethod
    def _structurally_implements_protocol(
            candidate: object, protocol_type: type[Any]
    ) -> tuple[bool, list[str]]:
        """
        Check the supported public-member contract on a class or supplied object.

        This is intentionally conservative and runtime-friendly:
        * It only verifies that all *public* attributes defined directly on the
          Protocol (non-underscore names) exist on the candidate.
        * If an attribute is callable on the Protocol, it must be present and
          callable on the candidate as well.
        * For an existing object, inspect the actual value so instance-only
          members and instance shadowing are respected without construction.

        It does NOT try to fully emulate static type-checking (mypy/pyright).
        Inherited Protocol members, annotation-only data and signature/type
        compatibility are outside this check. Normal attribute access may run
        user descriptors; errors other than missing attributes propagate.
        Admission checks the surface at bind time, not continuously at meld.

        Args:
            candidate (object): The implementation class or actual supplied value.
            protocol_type (type[Any]): The Protocol subclass being used as the
                spellframe.

        Returns:
            tuple[bool, list[str]]:
                - bool: True if the candidate passes the supported member checks.
                - list[str]: Missing or non-callable required member names.
        """
        missing: list[str] = []

        # Only inspect attributes defined directly on the Protocol; inherited
        # Protocol machinery and private members are ignored.
        for name, attr in protocol_type.__dict__.items():
            if name.startswith("_"):
                continue

            if not hasattr(candidate, name):
                missing.append(name)
                continue

            # If the Protocol member is callable, require the implementation
            # to also expose a callable with the same name.
            impl_attr = getattr(candidate, name, None)
            if callable(attr) and not callable(impl_attr):
                missing.append(name)

        return (len(missing) == 0, missing)

    #endregion Spell Inspector Helpers
#endregion Bind
