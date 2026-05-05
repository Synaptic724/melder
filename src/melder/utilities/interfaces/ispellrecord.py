from typing import Any, Optional, Protocol, Tuple, runtime_checkable
from melder.spellbook.existence.existence import Existence
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.ispelldescriptorpayload import ISpellDescriptorPayload

@runtime_checkable
class ISpellRecord(ICleanable, Protocol):
    """
    Descriptor-facing spell record contract.
    """

    nexus_label: str
    nexus_version: str
    origin_spellbook_id: str
    frame_name: str
    owner_conduit_id: Optional[str]
    spell_id: str
    spell_index_id: str
    spell_name: str
    spellframe: Any
    binding_name: Optional[str]
    permissions: Permissions
    existence: Existence
    payload: ISpellDescriptorPayload

    @property
    def record_key(self) -> Tuple[str, str]:
        """
        Return the canonical spell-record key.

        Returns:
            Tuple[str, str]: `(origin_spellbook_id, spell_id)`.
        """
        ...

    def get_configuration(self) -> 'IConfiguration':
        """
        Public API

        Returns the active configuration object for this Spellbook.

        Returns:
            IConfiguration: The configuration instance used by this
            Spellbook's Aether frame.
        """
        ...

    # ------------------------------------------------------------------
    # Conduit / cloning API
    # ------------------------------------------------------------------
    def create_new_preset_spellbook(self) -> "ISpellbook":
        """
        Internal

        Creates a new `Spellbook` instance that shares the same
        **Aether frame** and **Configuration** as the current
        Spellbook.

        Used internally when upgrading a lesser conduit into a normal
        conduit with a fresh Spellbook that reuses the existing frame +
        configuration.

        Returns:
            ISpellbook:
                A new Spellbook instance ready for use by a normal
                conduit.
        """
        ...

    def conjure(
            self,
            policy: Optional[str] = "automatic",
            name: Optional[str] = None,
            conduit_logger: Any | None = None,
    ) -> Any:
        """
        Public API

        Creates a new **Conduit** (execution channel) from this Spellbook.

        This method finalizes configuration (if needed), validates all
        local spells, and instantiates the Conduit.

        Args:
            policy:
                Spell access control behavior for this conduit.
                Must map to a `Policies` enum member (e.g. "automatic",
                "dynamic", "whitelist_all", "block_all").
            name:
                Optional name for the conduit.
            conduit_logger:
                Optional logger instance to attach to the Conduit.

        Returns:
            Any:
                The newly created Conduit instance.

        Raises:
            RuntimeError:
                If this Spellbook has already conjured a Conduit (only
                one allowed per Spellbook).
            RuntimeError:
                If dynamic policies are used while `system_state` is
                ``"automatic"``.
            ValueError:
                If configuration fails validation or the policy string is
                invalid.
        """
        ...
