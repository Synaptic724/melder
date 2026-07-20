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

    Registration:
        MELDER KERNEL - guarded. Produced by `FrameACLCompiler`; never
        user-constructed.

    Subsystem Context:
        The consumer-facing output of ACL compilation and the object the
        viewer, command, and codegen layers actually consult. A Rift stores it
        as projection state.

    System Context:
        "Contains only DERIVED ACCESS ANSWERS, never raw ACL config objects" is
        the boundary that makes this safe downstream. A consumer holding raw
        configuration could inspect or mutate policy while answering an
        authorization question; holding only answers means the worst it can do
        is read a verdict.
        Immutable-by-convention is the other half. Projection state is replaced
        WHOLESALE on refresh rather than edited in place, so a consumer
        mid-operation continues against a coherent surface instead of watching
        permissions shift under it. That is exactly why the Nexus refresh path
        blocks entrants and drains before applying new projections.
    """
    _ast_helper_access: str = "internal"
    __agent_purpose__: str = (
        "access: internal. CompiledFrameACLAccessSurface runtime object. Melder kernel machinery: "
        "read it to understand the runtime, do not drive it directly."
    )

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_frame_name",
        "_configuration_id",
        "_view_profile_name",
        "_view_profile_version",
        "_codegen_profile_name",
        "_codegen_profile_version",
        "_codegen_imports_enabled",
        "_allowed_import_module_roots",
        "_denied_import_module_roots",
        "_denied_builtin_names",
        "_codegen_unsafe_reflection_allowed",
        "_codegen_dunder_access_allowed",
        "_codegen_recursive_codegen_allowed",
        "_command_frame_enabled",
        "_allowed_kinds",
        "_allowed_commands",
        "_frame_payload_fields",
        "_visible_conduit_ids",
        "_visible_spell_keys",
        "_visible_spell_index_ids",
        "_enabled_conduit_ids",
        "_enabled_spell_index_ids",
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
            codegen_imports_enabled: bool = False,
            allowed_import_module_roots: Tuple[str, ...] = tuple(),
            denied_import_module_roots: Tuple[str, ...] = tuple(),
            denied_builtin_names: Tuple[str, ...] = tuple(),
            codegen_unsafe_reflection_allowed: bool = False,
            codegen_dunder_access_allowed: bool = False,
            codegen_recursive_codegen_allowed: bool = False,
            command_frame_enabled: bool = False,
            allowed_kinds: Tuple[str, ...],
            allowed_commands: Tuple[str, ...],
            frame_payload_fields: Tuple[str, ...],
            visible_conduit_ids: Tuple[str, ...],
            visible_spell_keys: Tuple[Tuple[str, str], ...],
            visible_spell_index_ids: Tuple[str, ...],
            enabled_conduit_ids: Tuple[str, ...] = tuple(),
            enabled_spell_index_ids: Tuple[str, ...] = tuple(),
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
            command_frame_enabled:
                True when frame-level command access is enabled.
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
            visible_spell_index_ids:
                Sorted visible spell index ids compiled from selector-aware
                spell visibility.
            enabled_conduit_ids:
                Sorted conduit ids enabled for command access.
            enabled_spell_index_ids:
                Sorted spell index ids enabled for command access.
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

        Returns:
            None.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._frame_name: str = frame_name
        self._configuration_id: str = configuration_id
        self._view_profile_name: str = view_profile_name
        self._view_profile_version: str = view_profile_version
        self._codegen_profile_name: str = codegen_profile_name
        self._codegen_profile_version: str = codegen_profile_version
        self._codegen_imports_enabled: bool = bool(codegen_imports_enabled)
        self._allowed_import_module_roots: Tuple[str, ...] = tuple(
            allowed_import_module_roots
        )
        self._denied_import_module_roots: Tuple[str, ...] = tuple(
            denied_import_module_roots
        )
        self._denied_builtin_names: Tuple[str, ...] = tuple(
            denied_builtin_names
        )
        self._codegen_unsafe_reflection_allowed: bool = bool(
            codegen_unsafe_reflection_allowed
        )
        self._codegen_dunder_access_allowed: bool = bool(
            codegen_dunder_access_allowed
        )
        self._codegen_recursive_codegen_allowed: bool = bool(
            codegen_recursive_codegen_allowed
        )
        self._command_frame_enabled: bool = bool(command_frame_enabled)
        self._allowed_kinds: Tuple[str, ...] = tuple(allowed_kinds)
        self._allowed_commands: Tuple[str, ...] = tuple(allowed_commands)
        self._frame_payload_fields: Tuple[str, ...] = tuple(frame_payload_fields)
        self._visible_conduit_ids: Tuple[str, ...] = tuple(visible_conduit_ids)
        self._visible_spell_keys: Tuple[Tuple[str, str], ...] = tuple(
            visible_spell_keys
        )
        self._visible_spell_index_ids: Tuple[str, ...] = tuple(
            visible_spell_index_ids
        )
        self._enabled_conduit_ids: Tuple[str, ...] = tuple(enabled_conduit_ids)
        self._enabled_spell_index_ids: Tuple[str, ...] = tuple(
            enabled_spell_index_ids
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

        Returns:
            None.
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

            del self._frame_name
            del self._configuration_id
            del self._view_profile_name
            del self._view_profile_version
            del self._codegen_profile_name
            del self._codegen_profile_version
            del self._codegen_imports_enabled
            del self._allowed_import_module_roots
            del self._denied_import_module_roots
            del self._denied_builtin_names
            del self._codegen_unsafe_reflection_allowed
            del self._codegen_dunder_access_allowed
            del self._codegen_recursive_codegen_allowed
            del self._command_frame_enabled
            del self._allowed_kinds
            del self._allowed_commands
            del self._frame_payload_fields
            del self._visible_conduit_ids
            del self._visible_spell_keys
            del self._visible_spell_index_ids
            del self._enabled_conduit_ids
            del self._enabled_spell_index_ids
            del self._conduit_payload_sections_by_id
            del self._spell_payload_sections_by_key
            del self._metadata
            del self._id
        del self._lock

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
    def codegen_imports_enabled(self) -> bool:
        """
        Return whether codegen import statements are enabled.

        Returns:
            bool: True when import statements are enabled.
        """
        self.check_cleaned()
        return self._codegen_imports_enabled

    @property
    def allowed_import_module_roots(self) -> Tuple[str, ...]:
        """
        Return the allowed import module roots for codegen validation.

        Returns:
            Tuple[str, ...]: Allowed import module roots.
        """
        self.check_cleaned()
        return self._allowed_import_module_roots

    @property
    def denied_import_module_roots(self) -> Tuple[str, ...]:
        """
        Return the denied import module roots for codegen validation.

        Returns:
            Tuple[str, ...]: Denied import module roots.
        """
        self.check_cleaned()
        return self._denied_import_module_roots

    @property
    def denied_builtin_names(self) -> Tuple[str, ...]:
        """
        Return builtin names denied to codegen validation/runtime.

        Returns:
            Tuple[str, ...]: Denied builtin names.
        """
        self.check_cleaned()
        return self._denied_builtin_names

    @property
    def codegen_unsafe_reflection_allowed(self) -> bool:
        """
        Return whether unsafe reflection is allowed for codegen.

        Returns:
            bool: True when unsafe reflection is allowed.
        """
        self.check_cleaned()
        return self._codegen_unsafe_reflection_allowed

    @property
    def codegen_dunder_access_allowed(self) -> bool:
        """
        Return whether dunder access is allowed for codegen.

        Returns:
            bool: True when dunder access is allowed.
        """
        self.check_cleaned()
        return self._codegen_dunder_access_allowed

    @property
    def codegen_recursive_codegen_allowed(self) -> bool:
        """
        Return whether recursive codegen is allowed.

        Returns:
            bool: True when recursive codegen is allowed.
        """
        self.check_cleaned()
        return self._codegen_recursive_codegen_allowed

    @property
    def command_frame_enabled(self) -> bool:
        """
        Return whether frame-level command access is enabled.

        Returns:
            bool: True when frame command access is enabled.
        """
        self.check_cleaned()
        return self._command_frame_enabled

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
    def visible_spell_index_ids(self) -> Tuple[str, ...]:
        """
        Return the visible spell index ids.

        Returns:
            Tuple[str, ...]: Visible stable spell lineage ids.
        """
        self.check_cleaned()
        return self._visible_spell_index_ids

    @property
    def enabled_conduit_ids(self) -> Tuple[str, ...]:
        """
        Return conduit ids enabled for command access.

        Returns:
            Tuple[str, ...]: Enabled conduit ids.
        """
        self.check_cleaned()
        return self._enabled_conduit_ids

    @property
    def enabled_spell_index_ids(self) -> Tuple[str, ...]:
        """
        Return spell index ids enabled for command access.

        Returns:
            Tuple[str, ...]: Enabled spell lineage ids.
        """
        self.check_cleaned()
        return self._enabled_spell_index_ids

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
