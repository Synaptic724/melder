from typing import Any, Optional, Union, Tuple
# Melder Imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.general_helpers import SpellInputUtils
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class SpellContract(Cleanable):
    """
    Intentional **late-binding contract socket** for **Dynamic Mode**.

    This is *not* a generic DI placeholder like `SpellMap`. It is a **contract
    declaration** that says:

        “At this location, I expect *some* spell that satisfies this
        frame/binding contract – but it may not exist in this Spellbook / Conduit
        yet. It will be wired in later via **conduit linking**.”

    Core intent
    -----------

    * **Dynamic Mode only**:
        - In **Automatic Mode**, using `SpellContract` should be treated as a
          configuration error. Automatic Mode expects everything to be resolved
          inside a single Spellbook at build time.
        - In **Dynamic Mode**, `SpellContract` is how you declare cross-Conduit,
          post-conjure dependencies that will be satisfied later.

    * **Late binding via Conduit links**:
        - When a Conduit is conjured, `SpellContract` sockets are recorded as
          *contract holes* in the graph.
        - At this point, the Spell may be marked as “contract-pending” in
          `SpellSystemState` / `SpellSystemStates`.
        - Later, when you **link Conduits** (e.g. `link_conduits(consumer, provider)`),
          the linker resolves these contracts by binding them to concrete spells
          from other Conduits and then triggers revalidation (Phases 5–7).

    * **Same construction shape as SpellMap, different semantics**:
        - `SpellMap`:
            - Normal in-Conduit DI placeholder.
            - Resolved eagerly (relative to its Spellbook) during normal builds.
        - `SpellContract`:
            - Contract socket for **cross-Conduit / late-bound wiring**.
            - Never treated as “just another SpellMap” by the pipeline.
            - Phases 5–7 treat these edges as contract-bearing and expect them
              to be satisfied by conduit linking.

    Typical Dynamic-mode usage
    --------------------------

        class ReportingService:
            def __init__(
                self,
                auth = SpellContract(
                    spellframe=IAuthService,
                    binding_name="primary",
                ),
            ):
                self._auth = auth

        # When `reporting_conduit` is conjured:
        #   - SpellCrafter sees SpellContract on `auth`.
        #   - A contract hole is recorded in the graph for that parameter.
        #   - SpellSystemStates marks the spell/Conduit as contract-pending.

        # Later, you link in an auth_conduit that provides an IAuthService:
        link_conduits(reporting_conduit, auth_conduit)

        # The linker finds a concrete spell in `auth_conduit` that satisfies
        # (IAuthService, "primary"), binds it to this SpellContract socket, and
        # revalidates the reporting graph.

    ─────────────────────────────────────────────
    ✅ Do NOT subclass SpellContract.
    ✅ Only use in Dynamic Mode when you *intend* to satisfy contracts later via conduit links.
    ✅ Use SpellMap for normal, in-Conduit DI.
    ─────────────────────────────────────────────
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + ["spell", "spellframe", "binding_name", "spell_override"]

    def __init__(
            self,
            spell: Any | None = None,
            *,
            spellframe: Optional[Any] = None,
            binding_name: Optional[str] = None,
            spell_override: Optional[Union[dict, list, tuple]] = None,
    ) -> None:
        """
        Create a new **late-binding contract socket**.

        Args:
            spell:
                Concrete spell implementation *if known up front*, or None for
                frame-only contracts.

                In Dynamic Mode, this is most often:

                    - None (frame-only contract to be satisfied by another Conduit),
                    - a class/type that *may* exist in another Conduit,
                    - or a Protocol used as the frame.

                The presence of `spell` does **not** force immediate resolution;
                it simply becomes part of the contract descriptor.

            spellframe:
                Optional logical interface / Protocol / frame key.

                In dynamic, cross-Conduit setups, this is typically the primary
                identity used to match a provider in another Conduit.

            binding_name:
                Optional binding name used to disambiguate multiple providers
                under the same frame. Normalized via SpellInputUtils so the
                contract is stable and case-insensitive. When None, the binding
                name remains None so default-binding semantics remain intact.

            spell_override:
                Optional positional/keyword override payload that should be
                applied when a concrete spell is finally bound to this contract
                during linking or resolution.

                Semantics mirror SpellMap:

                    - dict       → treated as keyword arguments
                    - list/tuple → treated as positional arguments

                `SpellContract` itself does *not* interpret this payload; it is
                carried forward so that the linker / runtime planning path can
                attach it to the eventual provider spell.

                When None, no override payload is attached.
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
        Explicitly release references and mark this contract as cleaned.

        Notes:
            - Idempotent: safe to call multiple times.
            - After cleanup, any attempt to use this contract should call
              `check_cleaned()` first (e.g., via properties) and will raise.
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
    # ------------------------------------------------------------------
    # Raw data for higher-level systems
    # ------------------------------------------------------------------
    @property
    def lookup_triplet(self) -> tuple[Any, Optional[Any], Optional[str]]:
        """
        Raw lookup data:

            (spell, spellframe, binding_name)

        This is what the Dynamic-mode contract pipeline consumes when:

            - capturing contract sockets during SpellCrafter analysis, and
            - later resolving them during conduit linking.

        Notes:
            - For frame-only contracts (`spell is None`), only `spellframe`
              and `binding_name` define the contract identity.
            - When `spell` is present, it is part of the contract descriptor but
              does *not* imply immediate resolution – the provider may live in
              another Conduit.
            - If a binding name was provided at construction time, it is
              normalized for case-insensitive matching.
        """
        return (self.spell, self.spellframe, self.binding_name)

    # ------------------------------------------------------------------
    # Canonical key (String-based) for Spellbook / contract maps
    # ------------------------------------------------------------------
    @property
    def canonical_key(self) -> Tuple[str, str]:
        """
        Canonical `(frame_key, binding_key)` for use in Spellbook / contract maps.

        This applies the same normalization as SpellMap:

            frame_key, bind_key = SpellInputUtils.normalize_spell_key(...)

        In practice, this becomes the **contract identity** used when:

            - indexing contract sockets in the Spellbook / SpellSystemStates, and
            - matching them against provider spells during conduit linking.
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
        Alias to `canonical_key` for compatibility with existing key logic.

        Treat this as the `(frame_key, binding_key)` contract identifier.
        """
        return self.canonical_key

    def __repr__(self) -> str:
        return (
            f"<SpellContract spell={self.spell!r} "
            f"spellframe={self.spellframe!r} "
            f"binding_name={self.binding_name!r} "
            f"override={self.spell_override!r}>"
        )
