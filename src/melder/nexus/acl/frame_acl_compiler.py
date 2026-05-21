import threading
from typing import TYPE_CHECKING, Dict, List, Optional, Set, Tuple
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.nexus.acl.frame_acl_compiled_access_surface import (
    CompiledFrameACLAccessSurface,
)
from melder.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.nexus.frame_descriptor.frame_descriptor import FrameDescriptor
from melder.utilities.helpers.general_helpers import SpellInputUtils
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.interfaces.iframeaclcodegenprofile import IFrameACLCodegenProfile
from melder.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.utilities.interfaces.iframeaclcommandprofile import IFrameACLCommandProfile
from melder.utilities.interfaces.iframeaclruleset import IFrameACLRuleSet

from melder.nexus.frame_descriptor.spell_record import SpellRecord
from melder.utilities.interfaces.iframeaclviewprofile import IFrameACLViewProfile

if TYPE_CHECKING:
    from melder.nexus.acl.configurations.profiles.builder.frame_acl_profile_builder import (
        FrameACLProfileBuilder,
    )


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
        "_lock",
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
        self._lock: threading.RLock = threading.RLock()
        self._profile_builder: IFrameACLProfileBuilder = profile_builder

    def cleanup(self) -> None:
        """
        Idempotently clear compiler-owned references.

        Contract:
            - Safe to call more than once.
            - Runs grouped teardown under the compiler-owned instance lock.
            - Drops only compiler-owned references.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            del self._profile_builder
            del self._id
            del self._lock

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
        view_precision_profile = (
            self._profile_builder.get_required_view_precision_profile(
                configuration.view_configuration.precision_profile_name
            )
            if configuration.view_configuration.precision_profile_name is not None
            else None
        )
        codegen_profile = self._profile_builder.get_required_codegen_profile(
            configuration.codegen_configuration.profile_name
        )
        codegen_precision_profile = (
            self._profile_builder.get_required_codegen_precision_profile(
                configuration.codegen_configuration.precision_profile_name
            )
            if configuration.codegen_configuration.precision_profile_name is not None
            else None
        )
        command_profile = self._profile_builder.get_required_command_profile(
            configuration.command_configuration.profile_name
        )
        command_precision_profile = (
            self._profile_builder.get_required_command_precision_profile(
                configuration.command_configuration.precision_profile_name
            )
            if configuration.command_configuration.precision_profile_name is not None
            else None
        )

        frame_payload_fields = self._compile_frame_payload_fields(
            view_profile,
            view_precision_profile,
            configuration,
        )
        visible_conduit_ids, conduit_payload_sections_by_id = (
            self._compile_conduit_access(
                frame_descriptor,
                view_profile,
                view_precision_profile,
                configuration,
            )
        )
        visible_spell_keys, visible_spell_index_ids, spell_payload_sections_by_key = (
            self._compile_spell_access(
                frame_descriptor,
                view_profile,
                view_precision_profile,
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
            codegen_precision_profile,
            configuration,
        )
        (
            command_frame_enabled,
            enabled_conduit_ids,
            enabled_spell_index_ids,
        ) = self._compile_command_enablement(
            frame_descriptor,
            command_profile,
            command_precision_profile,
            configuration,
        )
        (
            codegen_imports_enabled,
            allowed_import_module_roots,
            denied_import_module_roots,
        ) = self._compile_codegen_import_controls(
            codegen_profile,
            codegen_precision_profile,
            configuration,
        )
        denied_builtin_names = self._compile_codegen_builtin_controls(
            codegen_profile,
            codegen_precision_profile,
            configuration,
            imports_enabled=codegen_imports_enabled,
        )
        (
            codegen_unsafe_reflection_allowed,
            codegen_dunder_access_allowed,
        ) = self._compile_codegen_meta_controls(
            codegen_profile,
            codegen_precision_profile,
            configuration,
        )
        codegen_recursive_codegen_allowed = (
            self._compile_codegen_recursive_control(
                codegen_profile,
                codegen_precision_profile,
                configuration,
            )
        )

        metadata: Dict[str, object] = {
            "view_profile_name": view_profile.name,
            "view_profile_version": view_profile.version,
            "view_precision_profile_name": (
                view_precision_profile.name
                if view_precision_profile is not None
                else None
            ),
            "codegen_profile_name": codegen_profile.name,
            "codegen_profile_version": codegen_profile.version,
            "codegen_precision_profile_name": (
                codegen_precision_profile.name
                if codegen_precision_profile is not None
                else None
            ),
            "command_profile_name": command_profile.name,
            "command_profile_version": command_profile.version,
            "command_precision_profile_name": (
                command_precision_profile.name
                if command_precision_profile is not None
                else None
            ),
            "visible_conduit_count": len(visible_conduit_ids),
            "visible_spell_count": len(visible_spell_keys),
            "visible_spell_index_count": len(visible_spell_index_ids),
            "enabled_conduit_count": len(enabled_conduit_ids),
            "enabled_spell_index_count": len(enabled_spell_index_ids),
        }
        return CompiledFrameACLAccessSurface(
            frame_name=frame_descriptor.frame_name,
            configuration_id=configuration.configuration_id,
            view_profile_name=view_profile.name,
            view_profile_version=view_profile.version,
            codegen_profile_name=codegen_profile.name,
            codegen_profile_version=codegen_profile.version,
            codegen_imports_enabled=codegen_imports_enabled,
            allowed_import_module_roots=tuple(sorted(allowed_import_module_roots)),
            denied_import_module_roots=tuple(sorted(denied_import_module_roots)),
            denied_builtin_names=tuple(sorted(denied_builtin_names)),
            codegen_unsafe_reflection_allowed=codegen_unsafe_reflection_allowed,
            codegen_dunder_access_allowed=codegen_dunder_access_allowed,
            codegen_recursive_codegen_allowed=codegen_recursive_codegen_allowed,
            command_frame_enabled=command_frame_enabled,
            allowed_kinds=tuple(sorted(allowed_kinds)),
            allowed_commands=tuple(sorted(allowed_commands)),
            frame_payload_fields=tuple(sorted(frame_payload_fields)),
            visible_conduit_ids=tuple(sorted(visible_conduit_ids)),
            visible_spell_keys=tuple(sorted(visible_spell_keys)),
            visible_spell_index_ids=tuple(sorted(visible_spell_index_ids)),
            enabled_conduit_ids=tuple(sorted(enabled_conduit_ids)),
            enabled_spell_index_ids=tuple(sorted(enabled_spell_index_ids)),
            conduit_payload_sections_by_id=conduit_payload_sections_by_id,
            spell_payload_sections_by_key=spell_payload_sections_by_key,
            metadata=metadata,
        )

    @staticmethod
    def _compile_frame_payload_fields(
            view_profile: IFrameACLViewProfile,
            precision_profile: Optional[IFrameACLViewProfile],
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
            FrameACLCompiler._collect_effective_operation_effects_from_rulesets(
                view_profile.frame_ruleset,
                precision_profile.frame_ruleset if precision_profile is not None else None,
                FrameACLCompiler._as_frame_acl_ruleset(
                    configuration.view_configuration.frame_override_ruleset
                ),
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
            view_profile: IFrameACLViewProfile,
            precision_profile: Optional[IFrameACLViewProfile],
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
            FrameACLCompiler._collect_effective_operation_effects_from_rulesets(
                view_profile.conduit_ruleset,
                precision_profile.conduit_ruleset if precision_profile is not None else None,
                FrameACLCompiler._as_frame_acl_ruleset(
                    configuration.view_configuration.conduit_override_ruleset
                ),
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
            view_profile: IFrameACLViewProfile,
            precision_profile: Optional[IFrameACLViewProfile],
            configuration: FrameACLConfiguration,
    ) -> Tuple[
        Set[Tuple[str, str]],
        Set[str],
        Dict[Tuple[str, str], Tuple[str, ...]],
    ]:
        """
        Derive spell visibility and payload sections for one frame.

        Contract:
            - Returns both the visible spell-key set and the per-record payload
              section tuple visible under the effective ACL.
            - Also returns the visible stable `spell_index_id` set so later
              runtime consumers can target lineages directly.
            - Visibility is all-or-nothing per spell record in this first cut;
              the section tuple controls which payload slices are exposed.
            - Deny operations override allow operations.
        """
        visible_keys: Set[Tuple[str, str]] = set()
        visible_spell_index_ids: Set[str] = set()
        sections_by_key: Dict[Tuple[str, str], Tuple[str, ...]] = {}
        operation_to_section = {
            "show_binding_payload": "binding_payload",
            "show_resolution_payload": "resolution_payload",
            "show_class_profile": "class_profile",
            "show_callable_profile": "callable_profile",
            "show_metadata": "metadata",
            "show_instance_members": "instance_members",
            "show_dynamic_access": "dynamic_access",
        }
        spell_rulesets = (
            view_profile.spell_ruleset,
            precision_profile.spell_ruleset if precision_profile is not None else None,
            FrameACLCompiler._as_frame_acl_ruleset(
                configuration.view_configuration.spell_override_ruleset
            ),
        )
        selector_visible_rules_present = (
            FrameACLCompiler._spell_selector_rules_present_for_operation(
                "visible",
                *spell_rulesets,
            )
        )
        for record_key, spell_record in frame_descriptor.spell_records_by_key.items():
            if selector_visible_rules_present:
                selector_visible_allow, selector_visible_deny = (
                    FrameACLCompiler._collect_selector_spell_operation_effects_for_record(
                        "visible",
                        spell_record,
                        *spell_rulesets,
                    )
                )
                if "visible" in selector_visible_deny:
                    continue
                if "visible" not in selector_visible_allow:
                    continue
            else:
                allow_operations, deny_operations = (
                    FrameACLCompiler._collect_effective_spell_operation_effects_for_record(
                        spell_record,
                        *spell_rulesets,
                    )
                )
                if "visible" in deny_operations:
                    continue
                if "visible" not in allow_operations:
                    continue
            allow_operations, deny_operations = (
                FrameACLCompiler._collect_effective_spell_operation_effects_for_record(
                    spell_record,
                    *spell_rulesets,
                )
            )
            sections: List[str] = []
            for operation, section_name in operation_to_section.items():
                if operation in allow_operations and operation not in deny_operations:
                    sections.append(section_name)
            visible_keys.add(record_key)
            visible_spell_index_ids.add(spell_record.spell_index_id)
            sections_by_key[record_key] = tuple(sorted(sections))
        return visible_keys, visible_spell_index_ids, sections_by_key

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
            codegen_profile: IFrameACLCodegenProfile,
            precision_profile: Optional[IFrameACLCodegenProfile],
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
        for base_ruleset, precision_ruleset, override_ruleset in (
                (
                    codegen_profile.frame_ruleset,
                    precision_profile.frame_ruleset if precision_profile is not None else None,
                    FrameACLCompiler._as_frame_acl_ruleset(
                        configuration.codegen_configuration.frame_override_ruleset
                    ),
                ),
                (
                    codegen_profile.conduit_ruleset,
                    precision_profile.conduit_ruleset if precision_profile is not None else None,
                    FrameACLCompiler._as_frame_acl_ruleset(
                        configuration.codegen_configuration.conduit_override_ruleset
                    ),
                ),
                (
                    codegen_profile.spell_ruleset,
                    precision_profile.spell_ruleset if precision_profile is not None else None,
                    FrameACLCompiler._as_frame_acl_ruleset(
                        configuration.codegen_configuration.spell_override_ruleset
                    ),
                ),
                (
                    codegen_profile.capability_ruleset,
                    precision_profile.capability_ruleset if precision_profile is not None else None,
                    FrameACLCompiler._as_frame_acl_ruleset(
                        configuration.codegen_configuration.capability_override_ruleset
                    ),
                ),
        ):
            ruleset_allows, ruleset_denies = (
                FrameACLCompiler._collect_effective_operation_effects_from_rulesets(
                    base_ruleset,
                    precision_ruleset,
                    override_ruleset,
                )
            )
            allow_operations.update(ruleset_allows)
            deny_operations.update(ruleset_denies)
        return allow_operations.difference(deny_operations)

    @staticmethod
    def _compile_codegen_import_controls(
            codegen_profile: IFrameACLCodegenProfile,
            precision_profile: Optional[IFrameACLCodegenProfile],
            configuration: FrameACLConfiguration,
    ) -> Tuple[bool, Set[str], Set[str]]:
        """
        Derive codegen import posture from the capability ruleset family.

        Returns:
            Tuple[bool, Set[str], Set[str]]: Imports-enabled flag, allowed
                import roots, and denied import roots.
        """
        rulesets = (
            codegen_profile.capability_ruleset,
            precision_profile.capability_ruleset if precision_profile is not None else None,
            FrameACLCompiler._as_frame_acl_ruleset(
                configuration.codegen_configuration.capability_override_ruleset
            ),
        )
        allow_operations, deny_operations = (
            FrameACLCompiler._collect_effective_operation_effects_from_rulesets(
                *rulesets
            )
        )
        imports_enabled = (
            "enable_imports" in allow_operations
            and "enable_imports" not in deny_operations
        )
        (
            allowed_import_module_roots,
            denied_import_module_roots,
        ) = FrameACLCompiler._collect_import_module_roots_from_rulesets(*rulesets)
        if not imports_enabled:
            return False, set(), denied_import_module_roots
        return (
            True,
            allowed_import_module_roots.difference(denied_import_module_roots),
            denied_import_module_roots,
        )

    @staticmethod
    def _compile_codegen_builtin_controls(
            codegen_profile: IFrameACLCodegenProfile,
            precision_profile: Optional[IFrameACLCodegenProfile],
            configuration: FrameACLConfiguration,
            *,
            imports_enabled: bool,
    ) -> Set[str]:
        """
        Derive the denied builtin-name set for codegen validation/runtime.

        Returns:
            Set[str]: Denied builtin names.
        """
        rulesets = (
            codegen_profile.capability_ruleset,
            precision_profile.capability_ruleset if precision_profile is not None else None,
            FrameACLCompiler._as_frame_acl_ruleset(
                configuration.codegen_configuration.capability_override_ruleset
            ),
        )
        allowed_builtin_names, denied_builtin_names = (
            FrameACLCompiler._collect_condition_string_values_from_rulesets(
                "builtin_names",
                "builtin_names",
                *rulesets,
            )
        )
        final_denied_builtin_names: Set[str] = set(denied_builtin_names)
        if not imports_enabled:
            final_denied_builtin_names.add("__import__")
        return final_denied_builtin_names.difference(allowed_builtin_names)

    @staticmethod
    def _compile_codegen_meta_controls(
            codegen_profile: IFrameACLCodegenProfile,
            precision_profile: Optional[IFrameACLCodegenProfile],
            configuration: FrameACLConfiguration,
    ) -> Tuple[bool, bool]:
        """
        Derive reflection and dunder posture for codegen validation/runtime.

        Returns:
            Tuple[bool, bool]: Unsafe-reflection-allowed flag and
                dunder-access-allowed flag.
        """
        rulesets = (
            codegen_profile.capability_ruleset,
            precision_profile.capability_ruleset if precision_profile is not None else None,
            FrameACLCompiler._as_frame_acl_ruleset(
                configuration.codegen_configuration.capability_override_ruleset
            ),
        )
        allow_operations, deny_operations = (
            FrameACLCompiler._collect_effective_operation_effects_from_rulesets(
                *rulesets
            )
        )
        return (
            "unsafe_reflection" in allow_operations
            and "unsafe_reflection" not in deny_operations,
            "dunder_access" in allow_operations
            and "dunder_access" not in deny_operations,
        )

    @staticmethod
    def _compile_codegen_recursive_control(
            codegen_profile: IFrameACLCodegenProfile,
            precision_profile: Optional[IFrameACLCodegenProfile],
            configuration: FrameACLConfiguration,
    ) -> bool:
        """
        Derive whether recursive codegen is allowed.

        Returns:
            bool: True when recursive codegen is allowed.
        """
        rulesets = (
            codegen_profile.capability_ruleset,
            precision_profile.capability_ruleset if precision_profile is not None else None,
            FrameACLCompiler._as_frame_acl_ruleset(
                configuration.codegen_configuration.capability_override_ruleset
            ),
        )
        allow_operations, deny_operations = (
            FrameACLCompiler._collect_effective_operation_effects_from_rulesets(
                *rulesets
            )
        )
        return (
            "recursive_codegen" in allow_operations
            and "recursive_codegen" not in deny_operations
        )

    @staticmethod
    def _compile_command_enablement(
            frame_descriptor: FrameDescriptor,
            command_profile: IFrameACLCommandProfile,
            precision_profile: Optional[IFrameACLCommandProfile],
            configuration: FrameACLConfiguration,
    ) -> Tuple[bool, Set[str], Set[str]]:
        """
        Derive command enablement for frame/conduit/spell access paths.

        Returns:
            Tuple[bool, Set[str], Set[str]]: Frame enabled flag, enabled
                conduit ids, and enabled spell index ids.
        """
        frame_allows, frame_denies = (
            FrameACLCompiler._collect_effective_operation_effects_from_rulesets(
                command_profile.frame_ruleset,
                precision_profile.frame_ruleset if precision_profile is not None else None,
                FrameACLCompiler._as_frame_acl_ruleset(
                    configuration.command_configuration.frame_override_ruleset
                ),
            )
        )
        conduit_allows, conduit_denies = (
            FrameACLCompiler._collect_effective_operation_effects_from_rulesets(
                command_profile.conduit_ruleset,
                precision_profile.conduit_ruleset if precision_profile is not None else None,
                FrameACLCompiler._as_frame_acl_ruleset(
                    configuration.command_configuration.conduit_override_ruleset
                ),
            )
        )
        spell_rulesets = (
            command_profile.spell_ruleset,
            precision_profile.spell_ruleset if precision_profile is not None else None,
            FrameACLCompiler._as_frame_acl_ruleset(
                configuration.command_configuration.spell_override_ruleset
            ),
        )
        command_frame_enabled = (
            "enable" in frame_allows and "enable" not in frame_denies
        )
        enabled_conduit_ids: Set[str] = set()
        if "enable" in conduit_allows and "enable" not in conduit_denies:
            enabled_conduit_ids.update(frame_descriptor.conduit_records_by_id.keys())
        enabled_spell_index_ids: Set[str] = set()
        selector_enable_rules_present = (
            FrameACLCompiler._spell_selector_rules_present_for_operation(
                "enable",
                *spell_rulesets,
            )
        )
        for spell_record in frame_descriptor.spell_records_by_key.values():
            if selector_enable_rules_present:
                selector_enable_allow, selector_enable_deny = (
                    FrameACLCompiler._collect_selector_spell_operation_effects_for_record(
                        "enable",
                        spell_record,
                        *spell_rulesets,
                    )
                )
                if "enable" in selector_enable_deny:
                    continue
                if "enable" not in selector_enable_allow:
                    continue
            else:
                spell_allows, spell_denies = (
                    FrameACLCompiler._collect_effective_spell_operation_effects_for_record(
                        spell_record,
                        *spell_rulesets,
                    )
                )
                if "enable" in spell_denies:
                    continue
                if "enable" not in spell_allows:
                    continue
            enabled_spell_index_ids.add(spell_record.spell_index_id)
        return (
            command_frame_enabled,
            enabled_conduit_ids,
            enabled_spell_index_ids,
        )

    @staticmethod
    def _collect_operation_effects(
            ruleset: IFrameACLRuleSet,
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
            base_ruleset: IFrameACLRuleSet,
            override_ruleset: IFrameACLRuleSet,
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

    @staticmethod
    def _collect_effective_operation_effects_from_rulesets(
            *rulesets: Optional[IFrameACLRuleSet],
    ) -> Tuple[Set[str], Set[str]]:
        """
        Merge an ordered list of base/precision/override rulesets into one effect set.

        Returns:
            Tuple[Set[str], Set[str]]: Effective allow and deny operation names.
        """
        allow_operations: Set[str] = set()
        deny_operations: Set[str] = set()
        for ruleset in rulesets:
            if ruleset is None:
                continue
            ruleset_allows, ruleset_denies = (
                FrameACLCompiler._collect_operation_effects(
                    FrameACLCompiler._as_frame_acl_ruleset(ruleset)
                )
            )
            allow_operations.update(ruleset_allows)
            deny_operations.update(ruleset_denies)
        return allow_operations, deny_operations

    @staticmethod
    def _collect_condition_string_values_from_rulesets(
            operation_name: str,
            condition_key: str,
            *rulesets: Optional[IFrameACLRuleSet],
    ) -> Tuple[Set[str], Set[str]]:
        """
        Collect string condition values for one operation across rulesets.

        Args:
            operation_name:
                Operation name to match.
            condition_key:
                Condition key storing the string values to collect.
            *rulesets:
                Ordered rulesets to inspect.

        Returns:
            Tuple[Set[str], Set[str]]: Allowed and denied values.
        """
        allowed_values: Set[str] = set()
        denied_values: Set[str] = set()
        for ruleset in rulesets:
            if ruleset is None:
                continue
            for rule in FrameACLCompiler._as_frame_acl_ruleset(ruleset).rules_by_name.values():
                if rule.operation != operation_name:
                    continue
                condition_values = rule.conditions.get(condition_key, tuple())
                for value in condition_values:
                    if rule.effect == "allow":
                        allowed_values.add(value)
                    elif rule.effect == "deny":
                        denied_values.add(value)
        return allowed_values, denied_values

    @staticmethod
    def _collect_import_module_roots_from_rulesets(
            *rulesets: Optional[IFrameACLRuleSet],
    ) -> Tuple[Set[str], Set[str]]:
        """
        Collect import-module roots using narrowing intersection semantics.

        Contract:
            - Allowed import roots intersect across allow-bearing rulesets so
              precision profiles can narrow broader base profiles.
            - Denied import roots always union across the rulesets.

        Returns:
            Tuple[Set[str], Set[str]]: Allowed and denied import roots.
        """
        allowed_value_sets: List[Set[str]] = []
        denied_values: Set[str] = set()
        for ruleset in rulesets:
            if ruleset is None:
                continue
            ruleset_allowed_values: Set[str] = set()
            for rule in FrameACLCompiler._as_frame_acl_ruleset(ruleset).rules_by_name.values():
                if rule.operation != "import_modules":
                    continue
                module_roots = set(rule.conditions.get("module_roots", tuple()))
                if rule.effect == "allow":
                    ruleset_allowed_values.update(module_roots)
                elif rule.effect == "deny":
                    denied_values.update(module_roots)
            if len(ruleset_allowed_values) > 0:
                allowed_value_sets.append(ruleset_allowed_values)
        if len(allowed_value_sets) == 0:
            return set(), denied_values
        allowed_values = set(allowed_value_sets[0])
        for value_set in allowed_value_sets[1:]:
            allowed_values.intersection_update(value_set)
        return allowed_values, denied_values

    @staticmethod
    def _collect_effective_spell_operation_effects_for_record(
            spell_record: SpellRecord,
            *rulesets: Optional[IFrameACLRuleSet],
    ) -> Tuple[Set[str], Set[str]]:
        """
        Merge spell operations for one record using selector-aware spell rules.

        Returns:
            Tuple[Set[str], Set[str]]: Effective allow and deny operations for
                the target record.
        """
        allow_operations: Set[str] = set()
        deny_operations: Set[str] = set()
        for ruleset in rulesets:
            if ruleset is None:
                continue
            for rule in FrameACLCompiler._as_frame_acl_ruleset(ruleset).rules_by_name.values():
                if not FrameACLCompiler._spell_rule_matches_record(
                        rule.conditions,
                        spell_record,
                ):
                    continue
                if rule.effect == "allow":
                    allow_operations.add(rule.operation)
                elif rule.effect == "deny":
                    deny_operations.add(rule.operation)
        return allow_operations, deny_operations

    @staticmethod
    def _as_frame_acl_ruleset(ruleset: IFrameACLRuleSet) -> IFrameACLRuleSet:
        """
        Preserve the shared ruleset interface surface at existing call sites.

        Args:
            ruleset:
                Interface-typed ACL ruleset.

        Returns:
            IFrameACLRuleSet: The same ruleset object.
        """
        return ruleset

    @staticmethod
    def _spell_rule_matches_record(
            conditions: Dict[str, object],
            spell_record: SpellRecord,
    ) -> bool:
        """
        Return whether one spell rule condition set matches a spell record.

        Returns:
            bool: True when the selector is absent or matches the target record.
        """
        selector_keys = {
            "spell_id",
            "spell_index_id",
            "spellframe",
            "spell_name",
            "binding_name",
        }
        if not any(key in conditions for key in selector_keys):
            return True
        if (
                "spell_id" in conditions
                and conditions["spell_id"] != spell_record.spell_id
        ):
            return False
        if (
                "spell_index_id" in conditions
                and conditions["spell_index_id"] != spell_record.spell_index_id
        ):
            return False
        if "spellframe" in conditions:
            if spell_record.spellframe is None:
                return False
            if (
                    SpellInputUtils.normalize_frame_key(conditions["spellframe"]) !=
                    SpellInputUtils.normalize_frame_key(spell_record.spellframe)
            ):
                return False
        if "spell_name" in conditions:
            if str(conditions["spell_name"]).lower() != str(spell_record.spell_name).lower():
                return False
        if "binding_name" in conditions:
            if (
                    SpellInputUtils.normalize_binding_name(
                        conditions["binding_name"]
                    ) !=
                    SpellInputUtils.normalize_binding_name(
                        spell_record.binding_name
                    )
            ):
                return False
        return True

    @staticmethod
    def _spell_rule_has_selector(
            conditions: Dict[str, object],
    ) -> bool:
        """
        Return whether one spell rule condition set carries selector keys.

        Returns:
            bool: True when selector keys are present.
        """
        return any(
            key in conditions
            for key in (
                "spell_id",
                "spell_index_id",
                "spellframe",
                "spell_name",
                "binding_name",
            )
        )

    @staticmethod
    def _spell_selector_rules_present_for_operation(
            operation: str,
            *rulesets: Optional[IFrameACLRuleSet],
    ) -> bool:
        """
        Return whether any selector-aware rule exists for one spell operation.

        Returns:
            bool: True when selector-aware rules exist for the operation.
        """
        for ruleset in rulesets:
            if ruleset is None:
                continue
            for rule in FrameACLCompiler._as_frame_acl_ruleset(ruleset).rules_by_name.values():
                if (
                        rule.operation == operation and
                        FrameACLCompiler._spell_rule_has_selector(rule.conditions)
                ):
                    return True
        return False

    @staticmethod
    def _collect_selector_spell_operation_effects_for_record(
            operation: str,
            spell_record: SpellRecord,
            *rulesets: Optional[IFrameACLRuleSet],
    ) -> Tuple[Set[str], Set[str]]:
        """
        Collect selector-aware effects for one operation and spell record only.

        Returns:
            Tuple[Set[str], Set[str]]: Allow and deny operations from
                selector-aware rules matching the target record.
        """
        allow_operations: Set[str] = set()
        deny_operations: Set[str] = set()
        for ruleset in rulesets:
            if ruleset is None:
                continue
            for rule in FrameACLCompiler._as_frame_acl_ruleset(ruleset).rules_by_name.values():
                if rule.operation != operation:
                    continue
                if not FrameACLCompiler._spell_rule_has_selector(rule.conditions):
                    continue
                if not FrameACLCompiler._spell_rule_matches_record(
                        rule.conditions,
                        spell_record,
                ):
                    continue
                if rule.effect == "allow":
                    allow_operations.add(rule.operation)
                elif rule.effect == "deny":
                    deny_operations.add(rule.operation)
        return allow_operations, deny_operations

