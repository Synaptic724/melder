from typing import Any, Optional, Union, Tuple
# Melder Imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.general_helpers import SpellInputUtils
from melder.__melder_registration_guard__ import (
    __melder_registration_guard__ as _mrg,
)


class MutationContract(Cleanable):
    """
    Declarative mutation socket for mutation-research and AI-native experiments.

    `MutationContract` describes a dependency edge that belongs to the mutation
    system rather than ordinary DI wiring. It uses the same basic
    spell/frame/binding vocabulary as `SpellMap` and `SpellContract`, but its
    intent is different: it marks a host spell as participating in a mutation
    workflow where the effective provider may change or remain intentionally
    open.

    Current runtime status:

    - the descriptor still exists as part of the public contract surface
    - active usage is currently blocked by Phase 4 validation with
      `MUTATION_CONTRACT_DISABLED`
    - the docs therefore need to explain intended semantics without pretending
      the feature is fully enabled in normal runtime flows

    Conceptual model:

    - the descriptor is attached to an existing host spell
    - it identifies a mutation socket using spell/frame/binding data
    - it carries `late_binding` to distinguish between:
      - early-bound mutation intent, where a concrete replacement is expected
      - late-bound mutation intent, where the socket remains open and later
        overlays or mutation-promotion paths are expected to satisfy it

    This descriptor is not ordinary application DI. It belongs to
    MutationResearch-oriented experimentation and mutation governance.

    Contract:
        - Pure intent object; it does not perform mutation resolution itself.
        - Describes mutation-side provider identity plus optional override
          payload.
        - Cleanable and invalid after cleanup.
        - Documents an intended mutation surface even though the runtime
          currently gates active use behind `MUTATION_CONTRACT_DISABLED`.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "spell",
        "spellframe",
        "binding_name",
        "spell_override",
        "late_binding",
    ]

    def __init__(
        self,
        spell: Any | None = None,
        *,
        spellframe: Optional[Any] = None,
        binding_name: Optional[str] = None,
        spell_override: Optional[Union[dict, list, tuple]] = None,
        late_binding: bool = False,
    ) -> None:
        """
        Create one mutation-contract descriptor.

        Args:
            spell:
                Concrete mutation target if already known, or `None` for a
                frame-only mutation socket.

            spellframe:
                Optional logical interface, Protocol, or frame key used to
                describe the mutation-side provider identity.

            binding_name:
                Optional named binding used to disambiguate multiple providers
                under the same frame. Normalized via `SpellInputUtils` for
                case-insensitive matching. When `None`, default-binding semantics
                remain intact.

            spell_override:
                Optional override payload to apply if the mutation socket is
                eventually resolved to a concrete provider.

                Semantics mirror the other descriptor types:

                - `dict`: keyword arguments
                - `list` / `tuple`: positional arguments

                The descriptor stores this payload without interpreting it.

            late_binding:
                Whether the mutation socket is allowed to remain open without an
                immediate concrete provider.

                - `False`: expresses the stricter, early-bound posture where
                  mutation validation expects a concrete replacement path
                - `True`: expresses the looser, late-bound posture where the
                  socket identity is declared now and the concrete provider may
                  arrive through later mutation overlays or promotion flows

        Raises:
            ValueError: If both `spell` and `spellframe` are omitted, because
                the mutation socket would have no identity.
        """
        if spell is None and spellframe is None:
            raise ValueError(
                "MutationContract requires at least one of `spell` or `spellframe` "
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
        self.late_binding = late_binding

    def cleanup(self) -> None:
        """
        Release descriptor references and invalidate the mutation socket object.

        Contract:
            - Idempotent and safe to call multiple times.
            - Clears mutable override payloads before dropping references.
            - After cleanup the descriptor should be treated as unusable and
              callers should rely on `check_cleaned()` before reading it.
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
        Return the raw mutation-socket identity tuple.

        This is the shape higher mutation-aware layers consume before they
        derive a canonical key or interpret the current mutation socket.

        Returns:
            tuple[Any, Optional[Any], Optional[str]]: `(spell, spellframe,
            binding_name)` exactly as stored on the descriptor.
        """
        return (self.spell, self.spellframe, self.binding_name)

    @property
    def canonical_key(self) -> Tuple[str, str]:
        """
        Return the normalized mutation-socket identity pair.

        This uses the same normalization rules as `SpellMap` and
        `SpellContract`, yielding the stable `(frame_key, binding_key)` pair
        used by higher mutation-aware maps and comparisons.

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
            Tuple[str, str]: The same normalized key pair returned by
            `canonical_key`.
        """
        return self.canonical_key

    def __repr__(self) -> str:
        """
        Return a debug-oriented representation of the mutation descriptor.

        Returns:
            str: Representation showing stored spell/frame/binding/late-binding
            and override fields without attempting any mutation resolution.
        """
        return (
            f"<MutationContract spell={self.spell!r} "
            f"spellframe={self.spellframe!r} "
            f"binding_name={self.binding_name!r} "
            f"late_binding={self.late_binding!r} "
            f"override={self.spell_override!r}>"
        )
