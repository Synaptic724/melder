from typing import Any, Optional, Union, Tuple, ClassVar



# Melder Imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.general_helpers import SpellInputUtils


class SpellMap(Cleanable):
    """
    Declarative DI descriptor for normal spellbook-local resolution.

    `SpellMap` is the explicit descriptor form of ordinary Melder DI intent. It
    tells SpellCrafter and Meld which spell or frame/binding identity should be
    injected at a given parameter or attribute location, optionally along with
    an override payload that should be carried into runtime construction.

    Unlike `SpellContract`, this descriptor does not declare a cross-conduit
    hole that will be satisfied later. It stays inside the current resolution
    world. SpellCrafter and the runtime planning path inspect it, derive the
    canonical lookup identity, and then resolve a local spell through the usual
    Spellbook, SpellIndex, and Existence machinery.

    Supported shapes:

    - `SpellMap(MyService)`
      Direct type-based DI where the spell itself supplies the lookup identity.
    - `SpellMap(ILogic)`
      Frame-based DI where a Protocol / interface acts as the lookup frame.
    - `SpellMap(MyService, spellframe=ILogic, binding_name="primary")`
      Fully explicit spell + frame + binding declaration.
    - `SpellMap(spell=None, spellframe=ILogic, binding_name="primary")`
      Frame-only descriptor where the DI key is derived entirely from frame and
      binding.

    Typical usage:

    `python
    class MyService:
        def __init__(self, repo=SpellMap(MyRepo)):
            self.repo = repo

    class UsesLogic:
        def __init__(self, logic=SpellMap(ILogic, binding_name="primary")):
            self.logic = logic

    class UsesConfig:
        def __init__(
            self,
            cfg=SpellMap(
                spell=None,
                spellframe=IAppConfig,
                binding_name="primary",
            ),
        ):
            self.cfg = cfg
    `

    Contract:
        - Pure intent object; it does not resolve providers by itself.
        - Used for normal in-graph DI, not late conduit linking.
        - Carries spell/frame/binding identity plus optional override payload.
        - Cleanable and invalid after cleanup.
        - Should not be subclassed or treated like a runtime-resolved object.

    Threading:
        Value-shaped and effectively immutable after construction: the four
        slots are set in `__init__` and read thereafter. No lock is taken,
        because a descriptor written into a constructor default is shared
        read-only across every resolution that reads it.

    Lifecycle / Cleanup:
        Cleanable. The descriptor lives as long as the class default that
        declares it, which in practice is the lifetime of the defining module.

    Registration:
        MELDER KERNEL, USER-INSTANTIATED but NOT user-bindable. A user writes
        `SpellMap(MyRepo)` in their own constructor default constantly, so instances
        are authored outside melder - but binding the SpellMap CLASS itself is
        refused, which would be meaningless because a descriptor is a statement of
        intent, not a service to resolve.

    Subsystem Context:
        One of the two declarative DI descriptors, paired with `SpellContract`.
        The division is scope: `SpellMap` stays INSIDE the current resolution
        world and resolves through the ordinary Spellbook / SpellIndex /
        Existence machinery, while `SpellContract` declares a hole a future
        linked conduit may fill. Phase 1 classifies each parameter into a
        `ParameterDIShape`; a SpellMap default lands as `SPELLMAP_DEFAULT`, and
        Phase 3 performs the actual candidate resolution.

    System Context:
        The four supported shapes exist because DI identity in Melder is a
        (spell, frame, binding) triple rather than a single type key, and
        different call sites know different parts of it. Passing a concrete
        class supplies the whole identity; passing a Protocol supplies a frame
        and asks the graph to find the implementation; the frame-only form
        (`spell=None`) exists for the case where the caller deliberately knows
        NOTHING but the contract and the binding name.
        Ambiguity is a build-time failure, not a runtime one: a SpellMap
        default that resolves to zero or to multiple candidates raises rather
        than silently picking. That is the whole reason the explicit
        `binding_name` form exists - it is the documented way to disambiguate
        when several spells legitimately satisfy the same frame.
    """
    __ast_helper_access__: str = "public"
    __agent_purpose__: str = (
        "access: public. Declarative DI descriptor for normal in-graph resolution. Write it as a "
        "constructor default: SpellMap(MyRepo), SpellMap(ILogic, binding_name='primary'), or "
        "frame-only with spell=None. Zero or multiple matches raise at build time."
    )

    __slots__ = Cleanable.__slots__ + [
        "spell",
        "spellframe",
        "binding_name",
        "spell_override",
    ]

    def __init__(
        self,
        spell: Any | None = None,
        *,
        spellframe: Optional[Any] = None,
        binding_name: Optional[str] = None,
        spell_override: Optional[Union[dict, list, tuple]] = None,
    ) -> None:
        """
        Create one `SpellMap` declarative descriptor.

        Args:
            spell:
                Primary lookup target, or `None` for frame-only SpellMaps.

                When not `None`, this is typically:

                - the concrete implementation class
                - a Protocol used as a frame-like identity
                - a callable spell target
                - or another resolver-supported object

                Resolution semantics:

                - if `spellframe` is provided, the frame becomes the primary
                  grouping identity and `spell` acts as the concrete spell side
                  of the declaration
                - if `spellframe` is omitted, `spell` itself supplies the DI key
                - if `spell` is `None`, `spellframe` must be present and becomes
                  the sole DI identity

            spellframe:
                Optional logical interface, Protocol, or frame key used to
                group spells in Spellbook lookup space.

            binding_name:
                Optional named binding used to disambiguate multiple providers
                under the same frame. Normalized via `SpellInputUtils` for
                case-insensitive matching. When `None`, default-binding semantics
                remain intact.

            spell_override:
                Optional positional/keyword override payload propagated into the
                meld pipeline when the target creation is finally constructed.

                Semantics:

                - `dict`: keyword arguments
                - `list` / `tuple`: positional arguments

                The descriptor stores this payload without interpreting it.

        Raises:
            ValueError: If both `spell` and `spellframe` are omitted, because
                the descriptor would have no DI identity.

        Returns:
            None.
        """
        if spell is None and spellframe is None:
            raise ValueError(
                "SpellMap requires at least one of `spell` or `spellframe` "
                "to be provided."
            )
        super().__init__()
        self.spell = spell
        self.spellframe = spellframe
        self.binding_name = (
            SpellInputUtils.normalize_binding_name(binding_name)
            if binding_name is not None
            else None
        )
        # Preserve the caller payload; None means no override is attached.
        self.spell_override = spell_override

    def cleanup(self) -> None:
        """
        Release descriptor references and invalidate the object.

        Contract:
            - Idempotent and safe to call multiple times.
            - Clears mutable override payloads before dropping references.
            - After cleanup the descriptor should be treated as unusable and
              callers should rely on `check_cleaned()` before reading it.

        Returns:
            None.
        """
        if self._cleaned:
            return

        # No internal lock needed; this is a simple intent object.
        self._cleaned = True

        # Clear override payload if it is a container.
        if isinstance(self.spell_override, (list, dict)):
            self.spell_override.clear()

        self.spell_override = None
        self.spell = None
        self.spellframe = None
        self.binding_name = None

    @property
    def lookup_triplet(self) -> tuple[Any, Optional[Any], Optional[str]]:
        """
        Return the raw descriptor identity tuple.

        This is the shape SpellCrafter and the runtime planning path consume
        before they derive the normalized key or resolve the underlying spell.

        Contract:
            - Returns the RAW, AS-SUPPLIED triplet - the spell, spellframe and binding
              name exactly as the caller gave them, WITHOUT normalization.
            - This is NOT the registry key. Use `canonical_key` when you need the
              normalized identity the spellbook actually indexes by; the two can
              differ for the same SpellMap.

        Threading:
            Pure computation over immutable fields; safe from any thread.

        Lifecycle / Cleanup:
            Carries no cleaned-state guard.

        Returns:
            tuple[Any, Optional[Any], Optional[str]]: `(spell, spellframe,
            binding_name)` exactly as stored on the descriptor.

        Notes:
            - For frame-only SpellMaps (`spell is None`), only `spellframe` and
              `binding_name` contribute to the runtime identity.
            - For fully explicit SpellMaps, higher layers may use both `spell`
              and `spellframe` when enforcing resolution rules.
            - Binding names are already normalized when provided.
        """
        return (self.spell, self.spellframe, self.binding_name)

    @property
    def canonical_key(self) -> Tuple[str, str]:
        """
        Return the normalized `(frame_key, binding_key)` pair.

        This is the canonical Spellbook-style key derived through
        `SpellInputUtils.normalize_spell_key(...)`. It is the stable string pair
        higher layers use when indexing or matching SpellMap intent.

        Shape rules:

        - when `spellframe` is present, the frame key is derived from
          `spellframe`
        - when `spellframe` is absent, the frame key is derived from `spell`
        - binding defaults normalize to `"__default__"` inside the helper path

        Contract:
            - NORMALIZED identity: it runs the raw triplet through the shared key
              normalizer, so equivalent-but-differently-spelled inputs collapse to
              the same key. This is what the spellbook indexes by.
            - Recomputed on every access rather than cached, so it always reflects
              the current field values.

        Threading:
            Pure computation over immutable fields; safe from any thread.

        Lifecycle / Cleanup:
            Carries no cleaned-state guard.

        Returns:
            Tuple[str, str]: Normalized `(frame_key, binding_key)` pair.
        """
        frame_key, bind_key = SpellInputUtils.normalize_spell_key(
            spell=self.spell,
            spellframe=self.spellframe,
            binding_name=self.binding_name,
        )
        return frame_key, bind_key

    @property
    def spell_key(self) -> Tuple[str, str]:
        """
        Compatibility alias for `canonical_key`.

        Contract:
            - ALIAS for `canonical_key`, kept for call-site readability. Identical
              behaviour - it is the NORMALIZED key, not the raw triplet.

        Threading:
            Pure computation over immutable fields; safe from any thread.

        Lifecycle / Cleanup:
            Carries no cleaned-state guard.

        Returns:
            Tuple[str, str]: The same normalized key pair returned by
            `canonical_key`.
        """
        return self.canonical_key

    def __repr__(self) -> str:
        """
        Return a debug-oriented representation of the SpellMap descriptor.

        Contract:
            - Includes the override payload alongside the identity fields, so a `SpellMap`
              repr shows what it will DO as well as what it names.
            - Unguarded, unlike some other repr implementations in the codebase, so
              it stays safe to log.

        Threading:
            Pure computation over immutable fields; safe from any thread.

        Lifecycle / Cleanup:
            Carries no cleaned-state guard.

        Returns:
            str: Representation showing stored spell/frame/binding/override
            fields without performing any resolution.
        """
        return (
            f"<SpellMap spell={self.spell!r} "
            f"spellframe={self.spellframe!r} "
            f"binding_name={self.binding_name!r} "
            f"override={self.spell_override!r}>"
        )
