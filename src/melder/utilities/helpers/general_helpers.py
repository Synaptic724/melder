from enum import Enum
import inspect
from functools import lru_cache
from typing import Any, Optional, Tuple, Union, TypeVar, Type, ClassVar



T = TypeVar("T", bound=Enum)

class EnumHelpers:
    """

    Purpose:
        Small helper surface for enum normalization and validation, so callers
        can accept a raw string at an API boundary and still hold a real enum
        member internally.

    Responsibilities:
        - Convert raw string inputs into concrete enum members.
        - Reject values that do not name a member, loudly.

    Owned State:
        None. Static namespace, not an object with a lifetime.

    Threading:
        Stateless and therefore thread-safe.

    Lifecycle / Cleanup:
        No instances, no cleanup contract. Deliberately not `Cleanable`.

    Registration:
        MELDER KERNEL - guarded. A coercion namespace is called directly, never
        registered.

    Subsystem Context:
        One of the `utilities/helpers/` static namespaces beside `IDBuilder`
        (identity format), `SpellInputUtils` (lookup-key format), and
        `InitHelpers` (logger resolution). This one exists so the string ->
        enum boundary is enforced in one place rather than re-implemented at
        every public entry point that accepts a friendly string.

    System Context:
        `Spellbook.bind(...)` accepts permissions and existence as either enum
        members or strings and converts them here before anything downstream
        sees them. That is why the rest of the runtime can treat `Existence` and
        `Permissions` as genuinely typed: the coercion happened at the edge.

    Contract:
    - Converts raw string inputs into concrete enum members.
    - Returns already-normalized enum members unchanged when they belong to the
      requested enum type.
    - Raises immediately on `None`, incompatible types, or unknown values.
    """

    __ast_helper_access__: str = "public"
    __agent_purpose__: str = (
        "access: public. Static namespace for coercing raw strings into enum "
        "members at API boundaries. Call convert_enum_and_check(...) to accept "
        "a friendly string and hold a real member internally; unknown values "
        "refuse loudly rather than passing through."
    )

    @staticmethod
    # maxsize sized to the CLOSED vocabulary: 6 existences + 3 permissions
    # + policies/system states, as both string and member-passthrough keys.
    # 8 caused eviction churn on the exact path the cache exists to serve
    # (found 2026-07-19 during the strings-first UX ruling).
    @lru_cache(maxsize=64)
    def convert_enum_and_check(value: str | Enum, enum: Type[T]) -> T:
        """
        Convert one raw value into a concrete enum member of the requested type.

        Contract:
        - Accepts either a string or an enum member.
        - Returns the input unchanged when it is already an instance of the
          requested enum type.
        - Interprets string inputs by lowercased enum member name.

        Returns:
            T: The resolved enum member. Accepts a member or its string name and raises
                rather than guessing when the value does not map.

        Args:
            value:
                An enum member or its string name.
            enum:
                The enum class the value must resolve within.
        """
        if value is None:
            raise ValueError("Enum value cannot be None.")

        if isinstance(value, enum):
            return value

        if isinstance(value, str):
            try:
                return enum[value.lower()]
            except KeyError:
                valid_options = [e.name for e in enum]
                raise ValueError(
                    f"Invalid value '{value}' for enum {enum.__name__}. "
                    f"Expected one of: {valid_options}."
                )

        raise ValueError(
            f"Expected a string or {enum.__name__} member, got {type(value).__name__}."
        )

class SpellInputUtils:
    """
    SpellInputUtils
    ===============

    Canonical normalization utilities for spell identification in Melder.

    This class defines the *single source of truth* for how we turn:
        - spellframes (Protocols / interfaces / classes / strings)
        - spell names (class/function names)
        - binding names

    into **case-insensitive lookup keys** used by:

        - Spellbook (binding + lookup)
        - Bind (when constructing Spell._key)
        - Meld (when resolving a spell from (frame, binding_name))

    Design Rules
    ------------

    1. **Case-insensitive keys**:
       All keys are normalized to lowercase for lookups. Display names stay
       on the Spell itself (spell.spell_name, spell.spellframe, etc.).

    2. **Key shape matches Spellbook semantics**:
       We always build keys as:

           (frame_or_name, binding_name_or_default)

       where:
           frame_or_name     = spellframe if provided, else spell_name
           binding_name      = binding_name if provided, else "__default__"

       but both components are **lowercased** for the key.

    3. **Stable, deterministic**:
       The same spell + spellframe + binding_name will *always* normalize
       to the same (frame_key, binding_key) pair.

    4. **Separation of concerns**:
       - These helpers are for *keys only*.
       - Human-readable names live on Spell / SpellIndex and are not forced
         to lowercase there.

    Typical Usage
    -------------

    * When binding a spell (inside Spellbook / Bind):

        spell_name = type(spell).__name__ or spell.__name__
        key = SpellInputUtils.make_spell_key_from_parts(
            spellframe=spellframe,
            spell_name=spell_name,
            binding_name=binding_name,
        )

    * When resolving in Meld:

        frame_key, bind_key = SpellInputUtils.normalize_spell_key(
            spell=spell_obj_or_None,
            spellframe=spellframe,
            binding_name=binding_name,
        )

    After we wire this up, *all* spell key usage (bind + lookup) should
    flow through these helpers.

    Responsibilities:
        - Normalize the three parts of a spell address: frame key, spell name,
          binding name.
        - Compose those parts into the canonical `(frame_key, bind_key)` pair
          that bind and lookup both key on.
        - Supply the default binding name so nobody hardcodes it.

    WHY NORMALIZATION IS THE WHOLE POINT:
        Bind and lookup must agree EXACTLY or a spell becomes unfindable by the
        name it was registered under. Every address therefore passes through
        here rather than being assembled at each call site. `DEFAULT_BINDING_NAME`
        is public for the same reason: an unnamed binding has one spelling
        (`__default__`), and a call site inventing its own would silently miss.

    Owned State:
        None beyond the public `DEFAULT_BINDING_NAME` constant. Static
        namespace, not an object with a lifetime.

    Threading:
        Stateless and therefore thread-safe.

    Lifecycle / Cleanup:
        No instances, no cleanup contract. Deliberately not `Cleanable`.

    Registration:
        MELDER KERNEL - guarded. Address normalization is a runtime concern
        called directly, never registered.

    Subsystem Context:
        One of the `utilities/helpers/` static namespaces beside `IDBuilder`,
        `EnumHelpers`, and `InitHelpers`. The split from `IDBuilder` is
        deliberate and worth keeping straight: an ID NAMES one object; a KEY
        ADDRESSES a binding that may be satisfied by different objects over
        time. Conflating them would make renaming impossible.

    System Context:
        These keys are the resolution vocabulary of the DGR. `Bind` composes
        them at registration; `Meld` composes them again at resolve time
        through `_resolve_spell`; `SpellMap` and `SpellContract` express user
        intent in the same terms. Phase 4's duplicate-spell-name strategy exists
        precisely because two bindings normalizing to one key would make
        name-based resolution ambiguous.
    """

    __ast_helper_access__: str = "public"
    __agent_purpose__: str = (
        "access: public. Static namespace for spell address normalization. "
        "Compose (frame_key, bind_key) via normalize_spell_key(...) so bind and "
        "lookup agree exactly. Use DEFAULT_BINDING_NAME rather than hardcoding "
        "'__default__' - a call site inventing its own spelling silently misses."
    )

    # Public constant so everyone uses the same default
    DEFAULT_BINDING_NAME: ClassVar[str] = "__default__"

    # ------------------------------------------------------------------
    # Frame / name normalization
    # ------------------------------------------------------------------
    @staticmethod
    @lru_cache(maxsize=64)
    def normalize_frame_key(frame: Any) -> str:
        """
        Normalize a spellframe / frame identifier into a lowercase key.

        Inputs:
            - A Protocol class
            - A concrete class
            - A string frame name
            - Any other object (fallback to str(obj))

        Contract:
            - Lowercases the resolved name: a class/Protocol uses `__name__`, a
              string uses itself, anything else falls back to `str(frame)`.
              Cached (`lru_cache`), so repeated identical frames are cheap.

        Returns:
            str: Lowercased string used as the "frame" component of the key.

        Examples:
            ICache        -> "icache"
            "ICache"      -> "icache"
            MyService     -> "myservice"

        Args:
            frame:
                Frame identity - a type, Protocol, or string - to normalize.
        """
        if inspect.isclass(frame):
            raw = frame.__name__
        elif isinstance(frame, str):
            raw = frame
        else:
            raw = str(frame)
        return raw.lower()

    @staticmethod
    def normalize_spell_name(spell: Any) -> str:
        """
        Normalize a spell object into a canonical spell display name.

        This is primarily used as a fallback when no spellframe is passed in.

        Contract:
        - Prefers `__name__` when the object exposes one.
        - Falls back to `type(spell).__name__` for instances or anonymous
          callables.

        Returns:
            str: The spell name (NOT lowercased; this is a display name).

        Args:
            spell:
                Spell object whose name to derive (class/function/instance).
        """
        # This is for display/metadata; we don't lowercase here so that
        # spell.spell_name can remain pretty. The key path lowercases later.
        return getattr(spell, "__name__", type(spell).__name__)

    # ------------------------------------------------------------------
    # Binding name normalization
    # ------------------------------------------------------------------
    @staticmethod
    @lru_cache(maxsize=64)
    def normalize_binding_name(binding_name: Optional[str]) -> str:
        """
        Normalize a binding name into a lowercase key.

        If no binding name is provided, DEFAULT_BINDING_NAME ("__default__")
        is used.

        Contract:
            - Falsy input (None or empty) resolves to `DEFAULT_BINDING_NAME`
              ("__default__"); otherwise the name is lowercased. Cached
              (`lru_cache`).

        Returns:
            str: Lowercased binding name, or "__default__" if None/empty.

        Examples:
            None           -> "__default__"
            "Redis"        -> "redis"
            "MyVariant_01" -> "myvariant_01"

        Args:
            binding_name:
                Binding name to normalize, or None for default-binding semantics.
        """
        if not binding_name:
            return SpellInputUtils.DEFAULT_BINDING_NAME
        return binding_name.lower()

    # ------------------------------------------------------------------
    # Key construction helpers
    # ------------------------------------------------------------------
    @staticmethod
    def make_spell_key_from_parts(
            *,
            spellframe: Any | None,
            spell_name: str,
            binding_name: Optional[str],
    ) -> Tuple[str, str]:
        """
        Build a canonical (frame_key, binding_key) from explicit parts.

        This is the direct equivalent of the older Spellbook._make_spell_key,
        but with case-insensitive semantics baked in.

        Semantics:
            frame_base = spellframe if not None, else spell_name
            frame_key  = normalize_frame_key(frame_base)
            binding_key = normalize_binding_name(binding_name)

        Args:
            spellframe:
                The logical frame / interface / protocol. May be None.
            spell_name:
                The spell's explicit name (usually class.__name__).
            binding_name:
                Optional binding name (None means "__default__").

        Returns:
            Tuple[str, str]: (frame_key, binding_key)

        Raises:
            TypeError:
                Propagated if one of the underlying normalizers receives an
                incompatible value.
        """
        frame_base = spellframe if spellframe is not None else spell_name
        frame_key = SpellInputUtils.normalize_frame_key(frame_base)
        bind_key = SpellInputUtils.normalize_binding_name(binding_name)
        return frame_key, bind_key

    @staticmethod
    def normalize_spell_key(
            *,
            spell: Any | None = None,
            spellframe: Any | None = None,
            binding_name: Optional[str] = None,
    ) -> Tuple[str, str]:
        """
        Derive a canonical (frame_key, binding_key) using either a spell
        object or an explicit spellframe.

        This is the helper you want for most resolution cases (e.g. Meld).

        Resolution:
            1. spell_name = normalize_spell_name(spell) if spell is provided
            2. frame_base = spellframe if not None, else spell_name
            3. frame_key  = normalize_frame_key(frame_base)
            4. binding_key = normalize_binding_name(binding_name)

        At least ONE of (spell, spellframe) must be non-None. If both are
        None, a ValueError is raised.

        Args:
            spell:
                Optional spell object (class/function/instance). Used only
                to derive a name when spellframe is not supplied.
            spellframe:
                Optional frame/interface/protocol for grouping and DI keys.
            binding_name:
                Optional binding name; None means "__default__".

        Returns:
            Tuple[str, str]: (frame_key, binding_key)

        Raises:
            ValueError: If both `spell` and `spellframe` are None.
            TypeError:
                Propagated if one of the underlying normalizers receives an
                incompatible value.
        """
        if spell is None and spellframe is None:
            raise ValueError(
                "normalize_spell_key requires at least one of `spell` or `spellframe`."
            )

        spell_name: Optional[str] = None
        if spell is not None:
            spell_name = SpellInputUtils.normalize_spell_name(spell)

        frame_base = spellframe if spellframe is not None else spell_name
        frame_key = SpellInputUtils.normalize_frame_key(frame_base)
        bind_key = SpellInputUtils.normalize_binding_name(binding_name)
        return frame_key, bind_key
