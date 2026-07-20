from typing import Any, Optional, Union, Tuple, ClassVar



# Melder Imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.general_helpers import SpellInputUtils
from melder.__melder_registration_guard__ import (
    __melder_registration_guard__ as _mrg,
)


class SpellContract(Cleanable):
    """
    Declarative late-binding contract socket for dynamic conduit linking.

    `SpellContract` is not a generic in-spellbook DI placeholder like
    `SpellMap`. It declares that a parameter or field should eventually be
    satisfied by some spell matching a frame/binding contract, even if that
    provider does not exist in the current Spellbook or Conduit yet.

    In the runtime model, this descriptor marks a contract-bearing dependency:

    - during conjure/analysis, SpellCrafter records the socket as an unresolved
      contract edge rather than resolving it eagerly
    - during dynamic conduit linking, ConduitWard/linking flows look for a
      provider in another conduit that satisfies the same `(frame, binding)`
      identity
    - once a provider is linked, later validation phases rerun so the consumer
      graph is rebuilt against that now-satisfied contract

    This is why the descriptor is dynamic-mode only in practice. Automatic mode
    expects one self-contained Spellbook graph; `SpellContract` exists for
    cross-conduit, post-conjure wiring that is intentionally deferred.

    Relationship to neighboring descriptor types:

    - `SpellMap` expresses normal DI intent inside the current resolution
      world and is expected to resolve relative to the current spellbook graph
    - `SpellContract` expresses a late-bound dependency hole whose provider may
      arrive from another conduit later

    Typical usage:

    `python
    class ReportingService:
        def __init__(
            self,
            auth=SpellContract(
                spellframe=IAuthService,
                binding_name="primary",
            ),
        ):
            self._auth = auth
    `

    When the reporting conduit is conjured, the socket remains unresolved but
    explicitly declared. When a provider conduit is linked later, the linker
    can satisfy the contract and trigger revalidation of the reporting lineage.

    Contract:
        - Pure intent object; it does not perform linking or resolution itself.
        - Used to describe cross-conduit dependency identity.
        - Cleanable and invalid after cleanup.
        - Should not be subclassed or used as a substitute for `SpellMap` in
          ordinary in-conduit DI.

    Threading:
        Value-shaped and effectively immutable after construction: the four
        slots are set in `__init__` and read thereafter. No lock is taken,
        because a descriptor written into a constructor default is shared
        read-only across every resolution that reads it.

    Lifecycle / Cleanup:
        Cleanable. The descriptor lives as long as the class default that
        declares it, which in practice is the lifetime of the defining module.

    Registration:
        MELDER KERNEL - guarded, and USER-INSTANTIATED but NOT user-bindable.
        A user authors `SpellContract(spellframe=IAuthService)` in their own
        constructor default; the sentinel only stops anyone `bind()`-ing the
        SpellContract CLASS as a spell, which would be meaningless because a
        socket is a declaration of absence, not a service.

    Subsystem Context:
        The late-binding half of the descriptor pair. `SpellMap` resolves
        inside the current resolution world; this one declares an edge the
        graph deliberately CANNOT close yet. Phase 1 classifies it as the
        `SPELL_CONTRACT` parameter shape, Phase 4 validates the socket, and
        `ConduitWard` linking is what eventually satisfies it.

    System Context:
        The severity split in Phase 4 is the whole design in miniature. In
        AUTOMATIC mode an unsatisfied contract socket is an ERROR, because that
        mode promises one self-contained graph - a hole there can never be
        filled and the world is simply wrong. In DYNAMIC mode a missing
        provider is only a WARNING, because being unsatisfied is the expected
        intermediate state: the provider conduit may not be linked yet.
        The same asymmetry explains why linking is not merely a registry write.
        Satisfying a contract changes what the consumer graph resolves to, so
        `SpellSystemStates` marks contract dependents dirty and the consumer
        lineage re-runs its resolution phases against the now-satisfied edge.
        A contract is therefore a REVALIDATION TRIGGER, not just a lookup key -
        which is also why `SpellContract` requires at least a `spell` or a
        `spellframe`: with neither there is no identity for a future linker to
        match against, and the socket could never be closed.
    """
    __ast_helper_access__: str = "public"
    __agent_purpose__: str = (
        "access: public. Declares a LATE-BOUND dependency hole for dynamic conduit linking. Write it "
        "as a constructor default when the provider will arrive from another conduit. Requires at "
        "least spell or spellframe. Unsatisfied is an ERROR in automatic mode, a warning in dynamic."
    )

    __melder_internal__: ClassVar[object] = _mrg.sentinel
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
        Create one late-binding contract descriptor.

        Args:
            spell:
                Concrete spell implementation if known up front, or `None` for
                frame-only contracts.

                In dynamic linking flows this is most often:

                - `None` for a frame-only contract satisfied by another conduit
                - a class/type that may exist in another conduit
                - or a Protocol used as the frame

                The presence of `spell` does not force immediate resolution; it
                simply becomes part of the contract descriptor.

            spellframe:
                Optional logical interface, Protocol, or frame key.

                In dynamic, cross-conduit setups, this is typically the primary
                identity used to match a provider in another conduit.

            binding_name:
                Optional binding name used to disambiguate multiple providers
                under the same frame. Normalized via `SpellInputUtils` so the
                contract is stable and case-insensitive. When `None`, the
                binding name remains `None` so default-binding semantics remain
                intact.

            spell_override:
                Optional positional/keyword override payload that should be
                applied when a concrete spell is finally bound to this contract
                during linking or resolution.

                Semantics mirror `SpellMap`:

                - `dict`: treated as keyword arguments
                - `list` / `tuple`: treated as positional arguments

                `SpellContract` itself does not interpret this payload; it is
                carried forward so that the linker / runtime planning path can
                attach it to the eventual provider spell.

                When `None`, no override payload is attached.

        Raises:
            ValueError: If both `spell` and `spellframe` are omitted, because
                the contract would have no identity to match against.

        Returns:
            None.
        """
        if spell is None and spellframe is None:
            raise ValueError(
                "SpellContract requires at least one of `spell` or `spellframe` "
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
        Release descriptor references and invalidate the socket object.

        Contract:
            - Idempotent and safe to call multiple times.
            - Clears any mutable override payload before dropping references.
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
        Return the raw contract identity tuple.

        This is the descriptor shape consumed by the dynamic contract pipeline
        when it captures unresolved contract sockets during analysis and later
        tries to match them against linked provider spells.

        Returns:
            tuple[Any, Optional[Any], Optional[str]]: `(spell, spellframe,
            binding_name)` exactly as stored on the descriptor.

        Notes:
            - For frame-only contracts (`spell is None`), only `spellframe`
              and `binding_name` define the contract identity.
            - When `spell` is present, it is part of the contract descriptor
              but does not imply immediate resolution; the provider may live in
              another conduit.
            - If a binding name was provided at construction time, it is
              normalized for case-insensitive matching.
        """
        return (self.spell, self.spellframe, self.binding_name)

    @property
    def canonical_key(self) -> Tuple[str, str]:
        """
        Return the normalized contract identity used by runtime lookup tables.

        In practice this is the stable `(frame_key, binding_key)` pair used to:

        - index contract sockets in Spellbook / SpellSystemStates style maps
        - match a consumer contract hole against provider spells during conduit
          linking

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

        Returns:
            Tuple[str, str]: The same normalized contract identifier returned
            by `canonical_key`.
        """
        return self.canonical_key

    def __repr__(self) -> str:
        """
        Return a debug-oriented representation of the contract descriptor.

        Returns:
            str: Representation showing the stored spell/frame/binding/override
            fields without attempting any resolution.
        """
        return (
            f"<SpellContract spell={self.spell!r} "
            f"spellframe={self.spellframe!r} "
            f"binding_name={self.binding_name!r} "
            f"override={self.spell_override!r}>"
        )
