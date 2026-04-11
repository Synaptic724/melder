import threading
from typing import Dict, Optional, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class CompiledFrameACLAccessSurface(Cleanable):
    """
    Purpose:
        Hold one derived consumer-facing ACL access surface for a frame.

    Contract:
        - Contains only derived access answers, never raw ACL config objects.
        - Is immutable-by-convention after construction.
        - Uses an instance lock because cleanup clears grouped consumer-facing
          fields together in a nogil runtime.

    Lifecycle:
        Cleanup is idempotent and clears all owned derived data.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_surface_id",
        "_lock",
        "_frame_name",
        "_configuration_id",
        "_view_profile_name",
        "_view_profile_version",
        "_codegen_profile_name",
        "_codegen_profile_version",
        "_allowed_kinds",
        "_allowed_commands",
        "_frame_payload_fields",
        "_visible_conduit_ids",
        "_visible_spell_keys",
        "_conduit_payload_sections_by_id",
        "_spell_payload_sections_by_key",
        "_metadata",
    ]

    def __init__(
            self,
            *,
            frame_name: str,
            configuration_id: str,
            view_profile_name: str,
            view_profile_version: str,
            codegen_profile_name: str,
            codegen_profile_version: str,
            allowed_kinds: Tuple[str, ...],
            allowed_commands: Tuple[str, ...],
            frame_payload_fields: Tuple[str, ...],
            visible_conduit_ids: Tuple[str, ...],
            visible_spell_keys: Tuple[Tuple[str, str], ...],
            conduit_payload_sections_by_id: Dict[str, Tuple[str, ...]],
            spell_payload_sections_by_key: Dict[Tuple[str, str], Tuple[str, ...]],
            metadata: Optional[Dict[str, object]] = None,
    ) -> None:
        """
        Initialize one compiled frame ACL access surface.

        Args:
            frame_name:
                Frame name this surface applies to.
            configuration_id:
                Source ACL configuration id.
            view_profile_name:
                Effective reusable view profile name.
            view_profile_version:
                Effective reusable view profile version.
            codegen_profile_name:
                Effective reusable codegen profile name.
            codegen_profile_version:
                Effective reusable codegen profile version.
            allowed_kinds:
                Sorted visible kind names.
            allowed_commands:
                Sorted allowed command names.
            frame_payload_fields:
                Sorted frame payload fields currently visible.
            visible_conduit_ids:
                Sorted visible conduit ids.
            visible_spell_keys:
                Sorted visible spell record keys.
            conduit_payload_sections_by_id:
                Visible conduit payload sections keyed by conduit id.
            spell_payload_sections_by_key:
                Visible spell payload sections keyed by spell record key.
            metadata:
                Optional consumer-facing metadata map.
        Contract:
            - Stores only derived ACL answers, never raw config or descriptor
              objects.
            - Normalizes sequence/dict inputs into owned tuples and dictionaries
              so the surface remains value-oriented after compilation.
            - Captures the exact profile/config identity used to produce the
              compiled answers.
        """
        super().__init__()
        self._surface_id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._frame_name: str = frame_name
        self._configuration_id: str = configuration_id
        self._view_profile_name: str = view_profile_name
        self._view_profile_version: str = view_profile_version
        self._codegen_profile_name: str = codegen_profile_name
        self._codegen_profile_version: str = codegen_profile_version
        self._allowed_kinds: Tuple[str, ...] = tuple(allowed_kinds)
        self._allowed_commands: Tuple[str, ...] = tuple(allowed_commands)
        self._frame_payload_fields: Tuple[str, ...] = tuple(frame_payload_fields)
        self._visible_conduit_ids: Tuple[str, ...] = tuple(visible_conduit_ids)
        self._visible_spell_keys: Tuple[Tuple[str, str], ...] = tuple(
            visible_spell_keys
        )
        self._conduit_payload_sections_by_id: Dict[str, Tuple[str, ...]] = {
            conduit_id: tuple(sections)
            for conduit_id, sections in conduit_payload_sections_by_id.items()
        }
        self._spell_payload_sections_by_key: Dict[
            Tuple[str, str],
            Tuple[str, ...],
        ] = {
            record_key: tuple(sections)
            for record_key, sections in spell_payload_sections_by_key.items()
        }
        self._metadata: Dict[str, object] = dict(metadata) if metadata else {}

    def cleanup(self) -> None:
        """
        Idempotently clear the compiled access surface.

        Contract:
            - Safe to call more than once.
            - Clears owned derived dictionaries before dropping references.
            - Leaves future callers to fail through `check_cleaned()`.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._conduit_payload_sections_by_id.clear()
            self._spell_payload_sections_by_key.clear()
            self._metadata.clear()
            self._frame_name = None
            self._configuration_id = None
            self._view_profile_name = None
            self._view_profile_version = None
            self._codegen_profile_name = None
            self._codegen_profile_version = None
            self._allowed_kinds = None
            self._allowed_commands = None
            self._frame_payload_fields = None
            self._visible_conduit_ids = None
            self._visible_spell_keys = None
            self._conduit_payload_sections_by_id = None
            self._spell_payload_sections_by_key = None
            self._metadata = None
            self._surface_id = None
        self._lock = None

    @property
    def frame_name(self) -> str:
        """
        Return the frame name this compiled surface applies to.

        Returns:
            str: Target frame name.
        """
        self.check_cleaned()
        return self._frame_name

    @property
    def configuration_id(self) -> str:
        """
        Return the source ACL configuration id.

        Returns:
            str: Configuration id used to compile this surface.
        """
        self.check_cleaned()
        return self._configuration_id

    @property
    def view_profile_name(self) -> str:
        """
        Return the effective view profile name used during compilation.

        Returns:
            str: Effective view profile name.
        """
        self.check_cleaned()
        return self._view_profile_name

    @property
    def view_profile_version(self) -> str:
        """
        Return the effective view profile version used during compilation.

        Returns:
            str: Effective view profile version.
        """
        self.check_cleaned()
        return self._view_profile_version

    @property
    def codegen_profile_name(self) -> str:
        """
        Return the effective codegen profile name used during compilation.

        Returns:
            str: Effective codegen profile name.
        """
        self.check_cleaned()
        return self._codegen_profile_name

    @property
    def codegen_profile_version(self) -> str:
        """
        Return the effective codegen profile version used during compilation.

        Returns:
            str: Effective codegen profile version.
        """
        self.check_cleaned()
        return self._codegen_profile_version

    @property
    def allowed_kinds(self) -> Tuple[str, ...]:
        """
        Return the visible high-level kinds in this compiled surface.

        Returns:
            Tuple[str, ...]: Visible kind names such as frame/conduit/spell.
        """
        self.check_cleaned()
        return self._allowed_kinds

    @property
    def allowed_commands(self) -> Tuple[str, ...]:
        """
        Return the effective allowed command names.

        Returns:
            Tuple[str, ...]: Command names allowed by the compiled ACL.
        """
        self.check_cleaned()
        return self._allowed_commands

    @property
    def frame_payload_fields(self) -> Tuple[str, ...]:
        """
        Return the visible frame payload fields.

        Returns:
            Tuple[str, ...]: Frame payload field names visible to consumers.
        """
        self.check_cleaned()
        return self._frame_payload_fields

    @property
    def visible_conduit_ids(self) -> Tuple[str, ...]:
        """
        Return the visible conduit ids.

        Returns:
            Tuple[str, ...]: Conduit ids visible under the compiled ACL.
        """
        self.check_cleaned()
        return self._visible_conduit_ids

    @property
    def visible_spell_keys(self) -> Tuple[Tuple[str, str], ...]:
        """
        Return the visible spell record keys.

        Returns:
            Tuple[Tuple[str, str], ...]: Visible `(spellbook_id, spell_id)` keys.
        """
        self.check_cleaned()
        return self._visible_spell_keys

    @property
    def conduit_payload_sections_by_id(self) -> Dict[str, Tuple[str, ...]]:
        """
        Return conduit payload-section visibility keyed by conduit id.

        Contract:
            Returns a detached dictionary so callers cannot mutate internal
            section maps directly.

        Returns:
            Dict[str, Tuple[str, ...]]: Visible conduit payload sections.
        """
        self.check_cleaned()
        return dict(self._conduit_payload_sections_by_id)

    @property
    def spell_payload_sections_by_key(self) -> Dict[Tuple[str, str], Tuple[str, ...]]:
        """
        Return spell payload-section visibility keyed by spell record key.

        Contract:
            Returns a detached dictionary so callers cannot mutate internal
            section maps directly.

        Returns:
            Dict[Tuple[str, str], Tuple[str, ...]]: Visible spell payload sections.
        """
        self.check_cleaned()
        return dict(self._spell_payload_sections_by_key)

    @property
    def metadata(self) -> Dict[str, object]:
        """
        Return compiled-surface metadata.

        Contract:
            Returns a detached dictionary so callers cannot mutate internal
            metadata directly.

        Returns:
            Dict[str, object]: Consumer-facing compiled-surface metadata.
        """
        self.check_cleaned()
        return dict(self._metadata)
