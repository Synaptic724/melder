from typing import Dict

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.nexus.acl.frame_acl_compiled_access_surface import (
    CompiledFrameACLAccessSurface,
)
from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.aether.nexus.frame_descriptor.frame_descriptor import FrameDescriptor
from melder.aether.nexus.rift.frame_viewer.profiles.frame_viewer_profile import (
    FrameViewerProfile,
)
from melder.aether.nexus.rift.frame_viewer.profiles.general.view_conduit import (
    GeneralViewConduit,
)
from melder.aether.nexus.rift.frame_viewer.profiles.general.view_frame import (
    GeneralViewFrame,
)
from melder.aether.nexus.rift.frame_viewer.profiles.general.view_spell import (
    GeneralViewSpell,
)


class GeneralFrameViewerProfile(FrameViewerProfile):
    """
    Purpose:
        Represent the standard `general` viewer profile.

    Contract:
        - Composes one `view_frame`, `view_conduit`, and `view_spell` helper
          surface.
        - Stays bound by reference to one frame's descriptor + ACL state.
        - Routes tool ids to helper-object methods through dotted handler paths.

    Lifecycle:
        Cleanup is idempotent and cascades into the helper objects before the
        inherited profile cleanup clears the binding state.
    """

    __melder_internal__ = _mrg.sentinel
    _ast_helper_access: str = "public"
    __agent_purpose__: str = (
        "access: public. Standard bound viewer profile that composes the "
        "frame, conduit, and spell helper surfaces for one frame."
    )
    __slots__ = FrameViewerProfile.__slots__ + [
        "_view_frame",
        "_view_conduit",
        "_view_spell",
    ]

    def __init__(self) -> None:
        """
        Initialize the standard `general` viewer profile template.

        Returns:
            None.
        """
        super().__init__(
            "general",
            version="0.0.1",
            required_nexus_label="default",
            required_nexus_version="0.0.1",
            tool_handler_names_by_name=self._default_tool_handler_map(),
            default_grouping="frame",
            default_detail_level="detailed",
        )
        self._view_frame: GeneralViewFrame = GeneralViewFrame(
            frame_name=None,
            frame_descriptor=None,
            frame_acl_configuration=None,
            compiled_access_surface=None,
            default_detail_level=self.default_detail_level,
        )
        self._view_conduit: GeneralViewConduit = GeneralViewConduit(
            frame_view=self._view_frame,
        )
        self._view_spell: GeneralViewSpell = GeneralViewSpell(
            frame_view=self._view_frame,
        )

    @property
    def view_frame(self) -> GeneralViewFrame:
        """
        Return the frame-scoped helper surface.

        Returns:
            GeneralViewFrame: Frame helper surface.
        """
        self.check_cleaned()
        return self._view_frame

    @property
    def view_conduit(self) -> GeneralViewConduit:
        """
        Return the conduit-scoped helper surface.

        Returns:
            GeneralViewConduit: Conduit helper surface.
        """
        self.check_cleaned()
        return self._view_conduit

    @property
    def view_spell(self) -> GeneralViewSpell:
        """
        Return the spell-scoped helper surface.

        Returns:
            GeneralViewSpell: Spell helper surface.
        """
        self.check_cleaned()
        return self._view_spell

    def bind_to_frame(
            self,
            *,
            frame_name: str,
            frame_descriptor: FrameDescriptor,
            frame_acl_configuration: FrameACLConfiguration,
            compiled_access_surface: CompiledFrameACLAccessSurface,
    ) -> None:
        """
        Bind the profile and rebuild the helper surfaces.

        Args:
            frame_name:
                Target frame name.
            frame_descriptor:
                Descriptor truth for the frame.
            frame_acl_configuration:
                Current ACL configuration for the frame.
            compiled_access_surface:
                Compiled ACL surface for the frame.

        Returns:
            None.
        """
        super().bind_to_frame(
            frame_name=frame_name,
            frame_descriptor=frame_descriptor,
            frame_acl_configuration=frame_acl_configuration,
            compiled_access_surface=compiled_access_surface,
        )
        self._rebuild_helper_surfaces()

    def clone(self) -> "GeneralFrameViewerProfile":
        """
        Return one detached copy of the general profile template.

        Returns:
            GeneralFrameViewerProfile: Detached general profile copy.
        """
        self.check_cleaned()
        return GeneralFrameViewerProfile()

    def cleanup(self) -> None:
        """
        Idempotently clear the general profile and helper surfaces.

        Returns:
            None.
        """
        if self._cleaned:
            return
        if self._view_spell is not None:
            self._view_spell.cleanup()
            self._view_spell = None
        if self._view_conduit is not None:
            self._view_conduit.cleanup()
            self._view_conduit = None
        if self._view_frame is not None:
            self._view_frame.cleanup()
            self._view_frame = None
        super().cleanup()

    def _rebuild_helper_surfaces(self) -> None:
        """
        Rebuild helper surfaces against the currently bound frame state.

        Returns:
            None.
        """
        if self._view_spell is not None:
            self._view_spell.cleanup()
        if self._view_conduit is not None:
            self._view_conduit.cleanup()
        if self._view_frame is not None:
            self._view_frame.cleanup()
        self._view_frame = GeneralViewFrame(
            frame_name=self.bound_frame_name,
            frame_descriptor=self.frame_descriptor,
            frame_acl_configuration=self.frame_acl_configuration,
            compiled_access_surface=self.compiled_access_surface,
            default_detail_level=self.default_detail_level,
        )
        self._view_conduit = GeneralViewConduit(frame_view=self._view_frame)
        self._view_spell = GeneralViewSpell(frame_view=self._view_frame)

    @staticmethod
    def _default_tool_handler_map() -> Dict[str, str]:
        """
        Return the standard tool-to-helper routing map for `general`.

        Returns:
            Dict[str, str]: Standard `general` tool routing map.
        """
        return {
            "list_frames": "list_frame_names",
            "list_frame_ids": "list_frame_ids",
            "describe_viewer": "describe_viewer",
            "describe_current_frame": "describe_current_frame",
            "describe_frames_inventory": "describe_frames_inventory",
            "list_nexus_contracts": "list_nexus_contracts",
            "describe_frame_brief": "describe_frame_brief",
            "describe_host_inventory": "describe_host_inventory",
            "compare_frames_brief": "compare_frames_brief",
            "describe_viewer_method_surface": "describe_viewer_method_surface",
            "describe_agent_onboarding_json": "describe_agent_onboarding_json",
            "describe_viewer_agent_purpose_json": "describe_viewer_agent_purpose_json",
            "list_viewer_method_names_ast_json": "list_viewer_method_names_ast_json",
            "describe_viewer_class_surface_ast_json": "describe_viewer_class_surface_ast_json",
            "list_selected_profile_method_names_ast_json": "list_selected_profile_method_names_ast_json",
            "describe_selected_profile_class_surface_ast_json": "describe_selected_profile_class_surface_ast_json",
            "describe_selected_profile_agent_purpose_json": "describe_selected_profile_agent_purpose_json",
            "describe_selected_profile_helper_class_surfaces_ast_json": "describe_selected_profile_helper_class_surfaces_ast_json",
            "describe_selected_profile_helper_agent_purposes_json": "describe_selected_profile_helper_agent_purposes_json",
            "describe_selected_ast_surface_json": "describe_selected_ast_surface_json",
            "describe_frame": "describe_frame",
            "describe_frames": "describe_frames",
            "count_frames": "count_frames",
            "count_conduit_records": "count_conduit_records",
            "count_root_conduits": "count_root_conduits",
            "count_spell_records": "count_spell_records",
            "count_spellbooks": "count_spellbooks",
            "list_conduit_record_ids": "list_conduit_record_ids",
            "list_root_conduit_ids": "list_root_conduit_ids",
            "list_origin_spellbook_ids": "list_origin_spellbook_ids",
            "list_spell_record_ids": "list_spell_record_ids",
            "list_spell_record_keys": "list_spell_record_keys",
            "list_spell_names": "list_spell_names",
            "list_binding_names": "list_binding_names",
            "list_lineage_ids": "list_lineage_ids",
            "list_spellframes": "list_spellframes",
            "list_permissions": "list_permissions",
            "list_existence_kinds": "list_existence_kinds",
            "describe_descriptor_inventory": "describe_descriptor_inventory",
            "describe_descriptor_topology": "describe_descriptor_topology",
            "describe_conduit_records": "describe_conduit_records",
            "describe_spell_records": "describe_spell_records",
            "describe_spell_record": "describe_spell_record",
            "list_spells_by_owner_conduit_record": "list_spells_by_owner_conduit",
            "list_spells_by_spellbook_id_record": "list_spells_by_spellbook_id",
            "list_spells_by_permission_record": "list_spells_by_permission",
            "list_spells_by_existence_record": "list_spells_by_existence",
            "list_spells_by_spellframe_record": "list_spells_by_spellframe",
            "compare_frames": "compare_frames",
            "compare_frame_conduits": "compare_frame_conduits",
            "compare_frame_spells": "compare_frame_spells",
            "describe_binding_name_collisions": "describe_binding_name_collisions",
            "describe_spell_name_collisions": "describe_spell_name_collisions",
            "describe_lineage_groups": "describe_lineage_groups",
            "describe_spellframe_groups": "describe_spellframe_groups",
            "describe_spellbook_permission_mismatches": "describe_spellbook_permission_mismatches",
            "describe_spellbook_existence_mismatches": "describe_spellbook_existence_mismatches",
            "compare_spell_records": "compare_spell_records",
            "compare_conduit_records": "compare_conduit_records",
            "describe_visible_surface": "view_frame.describe_visible_surface",
            "describe_missing_surface": "view_frame.describe_missing_surface",
            "describe_frame_brief_local": "view_frame.describe_frame_brief",
            "describe_visible_inventory_by_kind": (
                "view_frame.describe_visible_inventory_by_kind"
            ),
            "describe_frame_topology": "view_frame.describe_frame_topology",
            "list_visible_target_ids": "view_frame.list_visible_target_ids",
            "list_visible_target_ids_by_kind": "view_frame.list_visible_target_ids_by_kind",
            "list_visible_conduit_ids": "view_frame.list_visible_conduit_ids",
            "list_visible_spell_source_ids": "view_frame.list_visible_spell_source_ids",
            "list_visible_root_conduits": "view_frame.list_visible_root_conduits",
            "list_visible_binding_names": "view_frame.list_visible_binding_names",
            "list_visible_spell_names": "view_frame.list_visible_spell_names",
            "list_visible_spellframes": "view_frame.list_visible_spellframes",
            "list_visible_lineage_ids": "view_frame.list_visible_lineage_ids",
            "describe_visible_spell_ownership": "view_frame.describe_visible_spell_ownership",
            "describe_visible_conduit_tree": "view_frame.describe_visible_conduit_tree",
            "search_targets_contains": "view_frame.search_targets_contains",
            "search_targets_prefix": "view_frame.search_targets_prefix",
            "group_targets_by_kind": "view_frame.group_targets_by_kind",
            "describe_target_brief": "view_frame.describe_target_brief",
            "describe_target_identity": "view_frame.describe_target_identity",
            "describe_visible_collisions": "view_frame.describe_visible_collisions",
            "describe_frame_payload": "view_frame.describe_frame_payload",
            "describe_frame_inventory": "view_frame.describe_frame_inventory",
            "describe_frame_access_contract": "view_frame.describe_frame_access_contract",
            "get_frame_payload_field": "view_frame.get_frame_payload_field",
            "find_target_by_display_name": "view_frame.find_target_by_display_name",
            "explain_target_access": "view_frame.explain_target_access",
            "list_targets": "view_frame.list_targets",
            "describe_targets": "view_frame.describe_targets",
            "list_conduits": "view_conduit.list_conduits",
            "list_root_conduits": "view_conduit.list_root_conduits",
            "describe_conduits": "view_conduit.describe_conduits",
            "get_conduit": "view_conduit.get_required_conduit",
            "describe_conduit": "view_conduit.describe_conduit",
            "describe_conduit_brief": "view_conduit.describe_conduit_brief",
            "describe_conduit_inventory": "view_conduit.describe_conduit_inventory",
            "describe_conduit_relationships": "view_conduit.describe_conduit_relationships",
            "describe_conduit_missing_sections": "view_conduit.describe_conduit_missing_sections",
            "describe_conduit_crosswalk": "view_conduit.describe_conduit_crosswalk",
            "list_conduit_spells": "view_conduit.list_conduit_spells",
            "describe_conduit_topology": "view_conduit.describe_conduit_topology",
            "compare_conduits": "view_conduit.compare_conduits",
            "is_root_conduit": "view_conduit.is_root_conduit",
            "get_root_conduit_id": "view_conduit.get_root_conduit_id",
            "list_conduits_by_root_id": "view_conduit.list_conduits_by_root_id",
            "list_conduits_by_policy": "view_conduit.list_conduits_by_policy",
            "list_conduits_by_state": "view_conduit.list_conduits_by_state",
            "list_peer_conduits": "view_conduit.list_peer_conduits",
            "list_peer_conduit_ids": "view_conduit.list_peer_conduit_ids",
            "list_spell_source_ids_for_conduit": "view_conduit.list_spell_source_ids_for_conduit",
            "list_binding_names_for_conduit": "view_conduit.list_binding_names_for_conduit",
            "list_spell_names_for_conduit": "view_conduit.list_spell_names_for_conduit",
            "find_conduit_by_name": "view_conduit.find_conduit_by_name",
            "explain_conduit_access": "view_conduit.explain_conduit_access",
            "describe_conduit_access_summary": "view_conduit.describe_conduit_access_summary",
            "get_conduit_payload_field": "view_conduit.get_conduit_payload_field",
            "list_spells": "view_spell.list_spells",
            "describe_spells": "view_spell.describe_spells",
            "get_spell": "view_spell.get_required_spell",
            "describe_spell": "view_spell.describe_spell",
            "describe_spell_brief": "view_spell.describe_spell_brief",
            "describe_spell_missing_sections": "view_spell.describe_spell_missing_sections",
            "describe_spell_identity": "view_spell.describe_spell_identity",
            "describe_spell_origin": "view_spell.describe_spell_origin",
            "describe_spell_lineage": "view_spell.describe_spell_lineage",
            "describe_spell_crosswalk": "view_spell.describe_spell_crosswalk",
            "describe_spell_binding": "view_spell.describe_spell_binding",
            "describe_spell_resolution": "view_spell.describe_spell_resolution",
            "describe_spell_metadata": "view_spell.describe_spell_metadata",
            "describe_spell_class_profile": "view_spell.describe_spell_class_profile",
            "describe_spell_callable_profile": "view_spell.describe_spell_callable_profile",
            "describe_spell_instance_members": "view_spell.describe_spell_instance_members",
            "describe_spell_dynamic_access": "view_spell.describe_spell_dynamic_access",
            "list_spell_dunder_member_names": "view_spell.list_spell_dunder_member_names",
            "describe_spell_dunder_members": "view_spell.describe_spell_dunder_members",
            "describe_spell_payload": "view_spell.describe_spell_payload",
            "describe_spell_detail": "view_spell.describe_spell_detail",
            "list_spells_by_payload_type": "view_spell.list_spells_by_payload_type",
            "list_spells_by_owner_conduit": "view_spell.list_spells_by_owner_conduit",
            "list_spells_by_spellbook_id": "view_spell.list_spells_by_spellbook_id",
            "list_spells_by_lineage_id": "view_spell.list_spells_by_lineage_id",
            "list_spells_by_permission": "view_spell.list_spells_by_permission",
            "list_spells_by_existence": "view_spell.list_spells_by_existence",
            "list_spells_by_spell_name": "view_spell.list_spells_by_spell_name",
            "list_spells_by_spellframe": "view_spell.list_spells_by_spellframe",
            "search_spells_contains": "view_spell.search_spells_contains",
            "search_spells_prefix": "view_spell.search_spells_prefix",
            "find_spell_by_binding_name": "view_spell.find_spell_by_binding_name",
            "explain_spell_access": "view_spell.explain_spell_access",
            "describe_spell_access_summary": "view_spell.describe_spell_access_summary",
            "compare_spells": "view_spell.compare_spells",
            "get_spell_payload_section": "view_spell.get_spell_payload_section",
        }


def create_general_profile() -> GeneralFrameViewerProfile:
    """
    Build the standard `general` viewer profile.

    Returns:
        GeneralFrameViewerProfile: Standard general viewer profile.
    """
    return GeneralFrameViewerProfile()
