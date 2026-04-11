from typing import Dict, List, Optional, Set, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.nexus.acl.frame_acl_compiled_access_surface import (
    CompiledFrameACLAccessSurface,
)
from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.aether.nexus.acl.profiles.frame_acl_codegen_profile import (
    FrameACLCodegenProfile,
)
from melder.aether.nexus.acl.profiles.frame_acl_ruleset import FrameACLRuleSet
from melder.aether.nexus.acl.profiles.frame_acl_view_profile import (
    FrameACLViewProfile,
)
from melder.aether.nexus.frame_descriptor.frame_descriptor import FrameDescriptor
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.interfaces.interfaces import IFrameACLProfileBuilder


class FrameACLCompiler(Cleanable):
    """
    Purpose:
        Compile typed ACL configuration over payload-backed descriptor records
        into a downstream consumer-facing access surface.

    Contract:
        - Consumes descriptor truth and ACL configuration only; never mutates
          descriptor state.
        - Resolves effective reusable profiles through the manager-owned profile
          builder/library.
        - Produces derived access answers suitable for downstream frame-link
          contract shaping.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_profile_builder",
    ]

    def __init__(self, profile_builder: IFrameACLProfileBuilder) -> None:
        """
        Initialize one ACL compiler.

        Args:
            profile_builder:
                Reusable ACL profile builder/library used to resolve effective
                view/codegen profiles by name.

        Returns:
            None.
        """
        super().__init__()
        if profile_builder is None:
            raise TypeError("profile_builder cannot be None.")
        self._id: str = IDBuilder.create_id()
        self._profile_builder: IFrameACLProfileBuilder = profile_builder

    def cleanup(self) -> None:
        """
        Idempotently clear compiler-owned references.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._profile_builder = None
        self._id = None

    def compile_frame_access_surface(
            self,
            frame_descriptor: FrameDescriptor,
            configuration: FrameACLConfiguration,
    ) -> CompiledFrameACLAccessSurface:
        """
        Compile one frame-local consumer-facing ACL access surface.

        Args:
            frame_descriptor:
                Descriptor truth for the target frame.
            configuration:
                Typed ACL configuration to compile.

        Returns:
            CompiledFrameACLAccessSurface: Derived consumer-facing access
            surface.
        """
        self.check_cleaned()
        if not isinstance(frame_descriptor, FrameDescriptor):
            raise TypeError("frame_descriptor must be a FrameDescriptor.")
        if not isinstance(configuration, FrameACLConfiguration):
            raise TypeError("configuration must be a FrameACLConfiguration.")

        view_profile = self._profile_builder.get_required_view_profile(
            configuration.view_configuration.profile_name
        )
        codegen_profile = self._profile_builder.get_required_codegen_profile(
            configuration.codegen_configuration.profile_name
        )

        frame_payload_fields = self._compile_frame_payload_fields(
            view_profile,
            configuration,
        )
        visible_conduit_ids, conduit_payload_sections_by_id = (
            self._compile_conduit_access(
                frame_descriptor,
                view_profile,
                configuration,
            )
        )
        visible_spell_keys, spell_payload_sections_by_key = (
            self._compile_spell_access(
                frame_descriptor,
                view_profile,
                configuration,
            )
        )
        allowed_kinds = self._compile_allowed_kinds(
            frame_payload_fields,
            visible_conduit_ids,
            visible_spell_keys,
        )
        allowed_commands = self._compile_allowed_commands(
            codegen_profile,
            configuration,
        )

        metadata = {
            "view_profile_name": view_profile.name,
            "view_profile_version": view_profile.version,
            "codegen_profile_name": codegen_profile.name,
            "codegen_profile_version": codegen_profile.version,
            "visible_conduit_count": len(visible_conduit_ids),
            "visible_spell_count": len(visible_spell_keys),
        }
        return CompiledFrameACLAccessSurface(
            frame_name=frame_descriptor.frame_name,
            configuration_id=configuration.configuration_id,
            view_profile_name=view_profile.name,
            view_profile_version=view_profile.version,
            codegen_profile_name=codegen_profile.name,
            codegen_profile_version=codegen_profile.version,
            allowed_kinds=tuple(sorted(allowed_kinds)),
            allowed_commands=tuple(sorted(allowed_commands)),
            frame_payload_fields=tuple(sorted(frame_payload_fields)),
            visible_conduit_ids=tuple(sorted(visible_conduit_ids)),
            visible_spell_keys=tuple(sorted(visible_spell_keys)),
            conduit_payload_sections_by_id=conduit_payload_sections_by_id,
            spell_payload_sections_by_key=spell_payload_sections_by_key,
            metadata=metadata,
        )

    @staticmethod
    def _compile_frame_payload_fields(
            view_profile: FrameACLViewProfile,
            configuration: FrameACLConfiguration,
    ) -> Set[str]:
        """
        Derive the frame-level payload fields visible under the effective view ACL.

        Contract:
            - Merges the reusable view profile rules with the configuration's
              frame override ruleset.
            - Returns an empty set when frame payload visibility is denied or
              not allowed.
            - Returns only descriptor payload field names, not raw payload
              values.
        """
        fields: Set[str] = set()
        allow_operations, deny_operations = (
            FrameACLCompiler._collect_effective_operation_effects(
                view_profile.frame_ruleset,
                configuration.view_configuration.frame_override_ruleset,
            )
        )
        if "show_payload" in allow_operations and "show_payload" not in deny_operations:
            fields.update({
                "system_state",
                "ai_native_enabled",
                "rift_enabled",
                "root_conduit_count",
                "root_conduit_ids",
                "named_root_conduits",
                "conduit_cloud_entry_count",
                "conduit_cloud_names",
                "cluster_count",
                "cluster_names",
            })
        return fields

    @staticmethod
    def _compile_conduit_access(
            frame_descriptor: FrameDescriptor,
            view_profile: FrameACLViewProfile,
            configuration: FrameACLConfiguration,
    ) -> Tuple[Set[str], Dict[str, Tuple[str, ...]]]:
        """
        Derive conduit visibility and conduit payload sections for one frame.

        Contract:
            - Returns both the visible conduit-id set and the per-conduit
              payload sections visible under the effective ACL.
            - Visibility is all-or-nothing per conduit in this first cut; the
              section tuple controls which conduit payload slices are exposed.
            - Deny operations override allow operations.
        """
        allow_operations, deny_operations = (
            FrameACLCompiler._collect_effective_operation_effects(
                view_profile.conduit_ruleset,
                configuration.view_configuration.conduit_override_ruleset,
            )
        )
        visible_ids: Set[str] = set()
        sections_by_id: Dict[str, Tuple[str, ...]] = {}
        if "visible" in deny_operations:
            return visible_ids, sections_by_id
        if "visible" not in allow_operations:
            return visible_ids, sections_by_id
        for conduit_id in frame_descriptor.conduit_records_by_id.keys():
            sections: List[str] = []
            if "show_payload" in allow_operations and "show_payload" not in deny_operations:
                sections.extend(["conduit_name", "conduit_state"])
            if "show_policy" in allow_operations and "show_policy" not in deny_operations:
                sections.append("policy")
            if "show_peer_links" in allow_operations and "show_peer_links" not in deny_operations:
                sections.append("peer_conduit_ids")
            visible_ids.add(conduit_id)
            sections_by_id[conduit_id] = tuple(sorted(sections))
        return visible_ids, sections_by_id

    @staticmethod
    def _compile_spell_access(
            frame_descriptor: FrameDescriptor,
            view_profile: FrameACLViewProfile,
            configuration: FrameACLConfiguration,
    ) -> Tuple[Set[Tuple[str, str]], Dict[Tuple[str, str], Tuple[str, ...]]]:
        """
        Derive spell visibility and payload sections for one frame.

        Contract:
            - Returns both the visible spell-key set and the per-record payload
              section tuple visible under the effective ACL.
            - Visibility is all-or-nothing per spell record in this first cut;
              the section tuple controls which payload slices are exposed.
            - Deny operations override allow operations.
        """
        allow_operations, deny_operations = (
            FrameACLCompiler._collect_effective_operation_effects(
                view_profile.spell_ruleset,
                configuration.view_configuration.spell_override_ruleset,
            )
        )
        visible_keys: Set[Tuple[str, str]] = set()
        sections_by_key: Dict[Tuple[str, str], Tuple[str, ...]] = {}
        if "visible" in deny_operations:
            return visible_keys, sections_by_key
        if "visible" not in allow_operations:
            return visible_keys, sections_by_key
        operation_to_section = {
            "show_binding_payload": "binding_payload",
            "show_resolution_payload": "resolution_payload",
            "show_class_profile": "class_profile",
            "show_callable_profile": "callable_profile",
            "show_metadata": "metadata",
            "show_instance_members": "instance_members",
            "show_dynamic_access": "dynamic_access",
        }
        for record_key in frame_descriptor.spell_records_by_key.keys():
            sections: List[str] = []
            for operation, section_name in operation_to_section.items():
                if operation in allow_operations and operation not in deny_operations:
                    sections.append(section_name)
            visible_keys.add(record_key)
            sections_by_key[record_key] = tuple(sorted(sections))
        return visible_keys, sections_by_key

    @staticmethod
    def _compile_allowed_kinds(
            frame_payload_fields: Set[str],
            visible_conduit_ids: Set[str],
            visible_spell_keys: Set[Tuple[str, str]],
    ) -> Set[str]:
        """
        Collapse compiled visibility sets into the high-level visible kinds set.

        Contract:
            Adds `"frame"`, `"conduit"`, and/or `"spell"` when the compiled
            payload/visibility outputs show that kind is visible at all.
        """
        allowed_kinds: Set[str] = set()
        if len(frame_payload_fields) > 0:
            allowed_kinds.add("frame")
        if len(visible_conduit_ids) > 0:
            allowed_kinds.add("conduit")
        if len(visible_spell_keys) > 0:
            allowed_kinds.add("spell")
        return allowed_kinds

    @staticmethod
    def _compile_allowed_commands(
            codegen_profile: FrameACLCodegenProfile,
            configuration: FrameACLConfiguration,
    ) -> Set[str]:
        """
        Derive the effective allowed command set for codegen/runtime consumers.

        Contract:
            - Merges frame, conduit, spell, and capability codegen rule
              families.
            - Applies deny operations after allow aggregation.
            - Returns command names only; call sites decide how those commands
              are interpreted.
        """
        allow_operations: Set[str] = set()
        deny_operations: Set[str] = set()
        for base_ruleset, override_ruleset in (
                (
                    codegen_profile.frame_ruleset,
                    configuration.codegen_configuration.frame_override_ruleset,
                ),
                (
                    codegen_profile.conduit_ruleset,
                    configuration.codegen_configuration.conduit_override_ruleset,
                ),
                (
                    codegen_profile.spell_ruleset,
                    configuration.codegen_configuration.spell_override_ruleset,
                ),
                (
                    codegen_profile.capability_ruleset,
                    configuration.codegen_configuration.capability_override_ruleset,
                ),
        ):
            ruleset_allows, ruleset_denies = (
                FrameACLCompiler._collect_effective_operation_effects(
                    base_ruleset,
                    override_ruleset,
                )
            )
            allow_operations.update(ruleset_allows)
            deny_operations.update(ruleset_denies)
        return allow_operations.difference(deny_operations)

    @staticmethod
    def _collect_operation_effects(
            ruleset: FrameACLRuleSet,
    ) -> Tuple[Set[str], Set[str]]:
        """
        Split one ruleset into allowed and denied operation sets.

        Contract:
            Reads only the rule effect/operation pairs and ignores other rule
            metadata.
        """
        allow_operations: Set[str] = set()
        deny_operations: Set[str] = set()
        for rule in ruleset.rules_by_name.values():
            if rule.effect == "allow":
                allow_operations.add(rule.operation)
            elif rule.effect == "deny":
                deny_operations.add(rule.operation)
        return allow_operations, deny_operations

    @staticmethod
    def _collect_effective_operation_effects(
            base_ruleset: FrameACLRuleSet,
            override_ruleset: FrameACLRuleSet,
    ) -> Tuple[Set[str], Set[str]]:
        """
        Merge base and override rulesets into effective allow/deny sets.

        Contract:
            Effective operations are the union of base and override allow/deny
            sets. Callers still apply deny-wins semantics at interpretation
            time.
        """
        base_allows, base_denies = FrameACLCompiler._collect_operation_effects(
            base_ruleset
        )
        override_allows, override_denies = (
            FrameACLCompiler._collect_operation_effects(override_ruleset)
        )
        return (
            base_allows.union(override_allows),
            base_denies.union(override_denies),
        )
