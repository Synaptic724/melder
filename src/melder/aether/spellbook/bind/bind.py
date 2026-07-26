import inspect
import threading
import hashlib
from typing import TYPE_CHECKING, Any, Optional, Sequence, Tuple, Union, ClassVar

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
from melder._build_assets._init_metadata.init_metadata import INTERNAL_MANIFEST
from melder.utilities.custom_exceptions.internal_registration_error import InternalRegistrationError


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
        The refusals are as load-bearing as the successes. Modules and Protocols
        are rejected as concrete spells because neither has a construction
        contract; method and lambda bindings are forced to `Existence.unique`
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
    ]

    def __init__(self, spellbook: Spellbook):
        """
        Initialize the spell registration gateway for one spellbook.

        Args:
            spellbook: Owning spellbook that will receive newly registered
                `Spell` instances.
        Contract:
            - Owns one `SpellExaminer` helper for profile creation.
            - Serializes registration work behind an internal lock.
            - Treats the supplied spellbook as the destination authority for
              all created spell bindings.

        Returns:
            None.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._spellbook: Spellbook = spellbook
        self._lock = threading.RLock()
        self._spell_examiner: SpellExaminer = SpellExaminer()

    def cleanup(self) -> None:
        """
        Cleans up resources held by the Bind instance.

        Bind itself does not own heavy resources beyond its lock, but we keep the
        cleanup pattern consistent with the rest of Melder. Once cleaned, the
        instance becomes inert and should not be reused.

        Contract:
        - Idempotent and lock-guarded.
        - Cleans the owned `SpellExaminer` before dropping references.
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
        del self._lock

    def bind(
            self,
            permissions: Permissions,
            existence: Existence,
            *,
            aetheric_frame: str,
            spell: Any = None,
            spellframe: Any = None,
            binding_name: Optional[str] = None,
            configured_disposal_method_names: Optional[frozenset[str]] = None,
            profile: str = "general",
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
            configured_disposal_method_names (Optional[frozenset[str]]): Names of methods to be considered for disposal.
        Contract:
            - When `spell` is omitted, returns a decorator that will bind the
              later target with the supplied policy and lifecycle settings.
            - When `spell` is supplied directly, runs the full binding pipeline
              immediately and returns the created `Spell`.
            - Decorator and direct-call modes are semantically equivalent once
              the target object is known.

        Returns:
            Union[Spell, Any]:
                - If used as a decorator, returns the decorated object.
                - If used as a direct call, returns the newly created `Spell` instance.
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
            configured_disposal_method_names: Optional[frozenset[str]] = None,
            profile: str = "general",
            **kwargs: Any,
    ) -> Spell:
        """
        Internal logic for processing the binding of a spell object.

        This method performs the full binding pipeline:
        * Validates existence and method/lambda constraints.
        * Enforces Protocol/Spellframe semantics:
          - Protocols cannot be bound as concrete spells.
          - Class-based spells bound under a Protocol spellframe must structurally
            implement that Protocol.
          - Method/lambda spells may also be grouped under Protocol or string
            spellframes (factory / handler semantics), but are not structurally
            validated against the Protocol.
        * Computes a deterministic fingerprint and SpellIndex from a `SpellBindingProfile`.
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

        Returns:
            Spell: The newly created and configured Spell instance.

        Raises:
            TypeError:
                - If a Protocol is bound directly as a concrete spell.
                - If a Protocol spellframe is provided for a class-based spell that
                  does not structurally implement it.
            ValueError:
                - If the binding is otherwise invalid (existence errors, lambda
                  without name, etc.).
        """
        with self._lock:
            # 0. Block registration of Melder internal objects/classes.
            assert_allowed(spell, context="bind")
            # 0.1 Reject modules outright.
            if inspect.ismodule(spell):
                raise TypeError(
                    f"Cannot bind module '{spell.__name__}'. Provide a class/function/object instead."
                )

            # ------------------------------------------------------------------
            # 1. Reject Protocols as concrete spells
            # ------------------------------------------------------------------
            # Protocols define *interfaces*, not constructible implementations.
            # Users may use Protocols as `spellframe` values, but cannot bind
            # a Protocol itself as a Spell.
            if Bind._is_protocol_type(spell):
                raise TypeError(
                    f"Cannot bind Protocol '{spell.__name__}' as a concrete spell. "
                    f"Protocols may only be used as spellframes (DI contracts)."
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
            resolved_disposal_method_names: frozenset[str] = frozenset()
            if (
                    configured_disposal_method_names
                    and isinstance(binding_profile, ClassBindingProfile)
            ):
                resolved_disposal_method_names = frozenset(
                    method_name
                    for method_name in binding_profile.method_names
                    if method_name in configured_disposal_method_names
                )
            fingerprint: str = Bind.sha256_profile(
                binding_profile,
                spellframe=spellframe,
                spell_name=spell_name,
                binding_name=binding_name,
                existence=existence,
                disposal_method_names=resolved_disposal_method_names,
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
            #   * For class-based spells: enforce structural implementation.
            #   * For callable spells: allow binding (factory/handler semantics),
            #     but do not run structural checks (no meaningful attribute set).
            if spellframe is not None and Bind._is_protocol_type(spellframe):
                if isinstance(binding_profile, ClassBindingProfile):
                    ok, missing_members = Bind._structurally_implements_protocol(
                        spell, spellframe
                    )
                    if not ok:
                        missing_str = ", ".join(sorted(missing_members))
                        raise TypeError(
                            f"Class '{spell_name}' does not structurally implement "
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
                # Owner ruling 2026-07-19: leftover bind kwargs flow into
                # Spell's OWN kwargs channel (Spell.__init__ stores them as
                # spell.metadata). Native params stay sovereign: a colliding
                # key fails loudly from Spell's signature.
                **kwargs,
            )

            provisional_general_profile.complete_with_spell(new_spell)

            return new_spell

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
            disposal_method_names (Sequence[str]): Names of methods to be considered for disposal.
        Contract:
            - Builds the same `SpellGeneralProfile` / `SpellBindingProfile`
              chain used by the real binding path.
            - Returns the same fingerprint that `_bind_logic(...)` would use
              when the same optional bind inputs are supplied.
            - Does not register anything into a spellbook or mutate runtime
              binding state.

        Returns:
            str: A unique identifier string (SHA256 hash) for the spell.
        """
        profile = SpellGeneralProfile.create_from_target(spell)
        return Bind.sha256_profile(
            profile.binding_profile,
            spellframe=spellframe,
            spell_name=spell_name,
            binding_name=binding_name,
            existence=existence,
            disposal_method_names=tuple(disposal_method_names),
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
            - Uses the explicit `v4-binding` schema prefix so future
              fingerprint-shape changes can version cleanly. v4 replaced the
              class source preview (first-5-lines text: docstring-sensitive,
              constructor-blind, and the only source-file read on the bind
              hot path) with the constructor signature string, so the
              fingerprint tracks exactly the shape compiled wiring depends
              on: constructor changes invalidate caches, docstring edits do
              not.
            - Includes the direct bind-time parameters that shape later
              compiler/runtime behavior: spell_name, spellframe, binding_name,
              existence, and resolved disposal metadata.
            - Equal bind signatures produce equal hashes; materially different
              signatures should produce different hashes.
        Returns:
            str: Deterministic SHA256 fingerprint for the supplied binding
                profile.
        """
        parts: list[str] = ["v4-binding"]  # fingerprint schema version

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
            cls: type, protocol_type: type[Any]
    ) -> tuple[bool, list[str]]:
        """
        Best-effort structural check that `cls` implements `protocol_type`.

        This is intentionally conservative and runtime-friendly:
        * It only verifies that all *public* attributes defined directly on the
          Protocol (non-underscore names) exist on the class.
        * If an attribute is callable on the Protocol, it must be present and
          callable on the class as well.

        It does NOT try to fully emulate static type-checking (mypy/pyright).
        The goal is simply to catch obvious mismatches where a class is bound
        under a Protocol spellframe but clearly does not implement the contract.

        Args:
            cls (type): The candidate implementation class.
            protocol_type (type[Any]): The Protocol subclass being used as the
                spellframe.

        Returns:
            tuple[bool, list[str]]:
                - bool: True if the class appears to implement the Protocol.
                - list[str]: The names of any missing members if the check fails.
        """
        missing: list[str] = []

        # Only inspect attributes defined directly on the Protocol; inherited
        # Protocol machinery and private members are ignored.
        for name, attr in protocol_type.__dict__.items():
            if name.startswith("_"):
                continue

            if not hasattr(cls, name):
                missing.append(name)
                continue

            # If the Protocol member is callable, require the implementation
            # to also expose a callable with the same name.
            impl_attr = getattr(cls, name, None)
            if callable(attr) and not callable(impl_attr):
                missing.append(name)

        return (len(missing) == 0, missing)

    #endregion Spell Inspector Helpers
#endregion Bind
