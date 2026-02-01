from typing import Any, Optional, Union, Tuple
# Melder Imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.general_helpers import SpellInputUtils
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class MutationContract(Cleanable):
    """
    Declarative **mutation socket** used for AI-native experimentation in
    **Dynamic mode**, scoped to the **MutationResearch** / mutation hub flows.

    NOTE: Mutation contracts are currently on hold; Phase 4 validation emits
    `MUTATION_CONTRACT_DISABLED` for any use of this descriptor.

    A MutationContract marks a parameter or field as being controlled by the
    mutation system rather than normal DI wiring. Conceptually:

        - It is always attached to an existing Spell (the "host" spell).
        - It behaves like a SpellMap/SpellContract in terms of how the target
          provider is described (spell / frame / binding).
        - It carries an explicit `late_binding` flag to signal whether the
          mutation is:

            * **early-bound** (late_binding=False):
                - The contract already points at a concrete replacement
                  implementation (and optional spell_override).
                - As soon as this MutationContract is attached, the host
                  spell’s DAG / DI shape is considered *mutated*.
                - Revalidation runs immediately and SpellSystemState flags
                  the host as a mutation candidate.

            * **late-bound** (late_binding=True):
                - The socket is a declared mutation hole with a known
                  contract shape (frame/binding), but no concrete target yet.
                - The host spell is still structurally valid, but gated by
                  mutation state until a value is supplied via spell_override
                  or a promoted mutation binding.
                - Revalidation sees the mutation socket and drives state
                  transitions in SpellSystemStates (e.g. mutation_candidate /
                  contract_unvalidated, etc.).

    Key points:

    - **AI-native only**:
        MutationContract is intended for AI-driven mutation pipelines (MutationResearch)
        and graph experiments, not normal application code.

    - **Dynamic mode only**:
        Automatic mode should treat the presence of MutationContract as
        illegal or a hard configuration error.

    - **Host-local mutation**:
        A MutationContract is allowed to change the host spell’s effective DAG
        shape and DI shape (new params, different provider topology, etc.),
        but it must not implicitly mutate or replace sub-spells beneath it;
        those must be mutated explicitly via their own MutationContracts.

    - **Spell override alignment**:
        The `spell_override` payload follows the same semantics as in SpellMap:
        it describes positional/keyword overrides for the mutated call. In late
        binding scenarios, the agent can provide or update these payloads over
        time to steer experiments without changing the host’s __init__ signature.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + ["spell", "spellframe", "binding_name", "spell_override", "late_binding"]

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
        Create a new MutationContract descriptor.

        Args:
            spell:
                Concrete spell target or None for frame-only mutation contracts.

            spellframe:
                Optional logical interface / Protocol / frame key.

            binding_name:
                Optional binding name to disambiguate under the same frame.
                When provided, this name is normalized via
                ``SpellInputUtils.normalize_binding_name`` so comparisons are
                case-insensitive. When None, the binding name remains None so
                default-binding semantics remain intact.

            spell_override:
                Optional override payload to apply when this mutation contract
                is resolved to a concrete provider. Semantics mirror SpellMap.

                When None, no override payload is attached.

            late_binding:
                When False:
                    - The mutation must be resolved during Phase 5–7
                      revalidation. An unresolved mutation is a structural
                      error / gating condition.

                When True:
                    - The contract may remain open (no concrete provider yet).
                    - Resolution is allowed to rely on mutation overlays /
                      spell_override at runtime to satisfy this socket.
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

        Used by mutation-aware resolution when deciding how to locate or
        declare the underlying mutation socket.
        Notes:
            - If a binding name was provided at construction time, it is
              normalized for case-insensitive matching.
        """
        return (self.spell, self.spellframe, self.binding_name)

    # ------------------------------------------------------------------
    # Canonical key for Spellbook / mutation maps
    # ------------------------------------------------------------------
    @property
    def canonical_key(self) -> Tuple[str, str]:
        """
        Canonical `(frame_key, binding_key)` for use in maps.

        Same normalization rules as SpellMap / SpellContract.
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
        Alias to `canonical_key` for compatibility with SpellMap-style usage.
        """
        return self.canonical_key

    def __repr__(self) -> str:
        return (
            f"<MutationContract spell={self.spell!r} "
            f"spellframe={self.spellframe!r} "
            f"binding_name={self.binding_name!r} "
            f"late_binding={self.late_binding!r} "
            f"override={self.spell_override!r}>"
        )
