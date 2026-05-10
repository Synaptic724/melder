import threading
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
        "_lock",
        "_spell",
        "_spellframe",
        "_binding_name",
        "_spell_override",
        "_late_binding",
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
        self._lock: threading.RLock = threading.RLock()
        self._spell = spell
        self._spellframe = spellframe
        self._binding_name = (
            SpellInputUtils.normalize_binding_name(binding_name)
            if binding_name is not None
            else None
        )
        # Preserve the caller payload; None means no override is attached.
        self._spell_override = spell_override
        self._late_binding = late_binding

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

        with self._lock:
            if self._cleaned:
                return

            self._cleaned = True

            # Clear override payload if it is a container.
            if isinstance(self._spell_override, (list, dict)):
                self._spell_override.clear()

            self._spell_override = None
            self._spell = None
            self._spellframe = None
            self._binding_name = None
            self._late_binding = None

        self._lock = None


    @property
    def spell(self) -> Any:
        """
        Return the concrete spell target currently stored on this contract.

        Returns:
            Any: Current concrete spell target, or `None` when this is a
                frame-only mutation socket.
        """
        self.check_cleaned()
        with self._lock:
            return self._spell

    @property
    def spellframe(self) -> Optional[Any]:
        """
        Return the logical frame/protocol target currently stored on this contract.

        Returns:
            Optional[Any]: Current logical frame/protocol target, or `None`.
        """
        self.check_cleaned()
        with self._lock:
            return self._spellframe

    @property
    def binding_name(self) -> Optional[str]:
        """
        Return the normalized binding name currently stored on this contract.

        Returns:
            Optional[str]: Normalized binding name, or `None` when the
                descriptor uses default-binding semantics.
        """
        self.check_cleaned()
        with self._lock:
            return self._binding_name

    @property
    def spell_override(self) -> Optional[Union[dict, list, tuple]]:
        """
        Return the current override payload stored on this contract.

        Returns:
            Optional[Union[dict, list, tuple]]: Current override payload as
                stored on the descriptor.
        """
        self.check_cleaned()
        with self._lock:
            return self._spell_override

    @property
    def late_binding(self) -> bool:
        """
        Return whether this mutation socket is allowed to remain unresolved.

        Returns:
            bool: Current late-binding posture for the descriptor.
        """
        self.check_cleaned()
        with self._lock:
            return self._late_binding

    def update_contract(
        self,
        *,
        spell: Any = ...,
        spellframe: Any = ...,
        binding_name: Any = ...,
        spell_override: Any = ...,
        late_binding: Any = ...,
    ) -> None:
        """
        Update the live in-memory mutation-contract identity under a lock.

        Purpose:
            Provide one supported mutation path for the descriptor instead of
            relying on direct unsynchronized field assignment.

        Contract:
            - Applies updates atomically under the internal `RLock`.
            - Preserves current values for any field not explicitly supplied.
            - Re-normalizes `binding_name` when a new value is provided.
            - Rejects updates that would leave both `spell` and `spellframe`
              unset.

        Args:
            spell:
                New concrete spell target, or `...` to keep the current value.
            spellframe:
                New logical frame/protocol target, or `...` to keep the
                current value.
            binding_name:
                New binding name, or `...` to keep the current value. When a
                concrete value is provided it is normalized through
                `SpellInputUtils.normalize_binding_name(...)`. `None` clears the
                explicit binding name and restores default-binding semantics.
            spell_override:
                New override payload, or `...` to keep the current payload.
            late_binding:
                New late-binding posture, or `...` to keep the current value.

        Returns:
            None.

        Raises:
            ValueError:
                If the update would leave the descriptor without both `spell`
                and `spellframe`.
        """
        self.check_cleaned()
        with self._lock:
            self.check_cleaned()

            new_spell = self._spell if spell is ... else spell
            new_spellframe = self._spellframe if spellframe is ... else spellframe
            if new_spell is None and new_spellframe is None:
                raise ValueError(
                    "MutationContract requires at least one of `spell` or `spellframe` "
                    "to be provided."
                )

            if binding_name is ...:
                new_binding_name = self._binding_name
            elif binding_name is None:
                new_binding_name = None
            else:
                new_binding_name = SpellInputUtils.normalize_binding_name(binding_name)

            self._spell = new_spell
            self._spellframe = new_spellframe
            self._binding_name = new_binding_name
            if spell_override is not ...:
                self._spell_override = spell_override
            if late_binding is not ...:
                self._late_binding = late_binding

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
        self.check_cleaned()
        with self._lock:
            return (self._spell, self._spellframe, self._binding_name)

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
        self.check_cleaned()
        with self._lock:
            spell = self._spell
            spellframe = self._spellframe
            binding_name = self._binding_name
        frame_key, bind_key = SpellInputUtils.normalize_spell_key(
            spell=spell,
            spellframe=spellframe,
            binding_name=binding_name,
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
        self.check_cleaned()
        return self.canonical_key

    def __repr__(self) -> str:
        """
        Return a debug-oriented representation of the mutation descriptor.

        Returns:
            str: Representation showing stored spell/frame/binding/late-binding
            and override fields without attempting any mutation resolution.
        """
        self.check_cleaned()
        with self._lock:
            spell = self._spell
            spellframe = self._spellframe
            binding_name = self._binding_name
            late_binding = self._late_binding
            spell_override = self._spell_override
        return (
            f"<MutationContract spell={spell!r} "
            f"spellframe={spellframe!r} "
            f"binding_name={binding_name!r} "
            f"late_binding={late_binding!r} "
            f"override={spell_override!r}>"
        )