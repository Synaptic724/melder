import threading
from typing import Callable, Dict, List, Optional

from melder.nexus.acl.validator.compatibility.frame_acl_set_compatibility_validator import (
    FrameACLSetCompatibilityValidator,
)
from melder.nexus.acl.configurations.profiles.builder.frame_acl_profile_builder import (
    FrameACLProfileBuilder,
)
from melder.utilities.general_base.cleanable import Cleanable

from melder.nexus.acl.builder.frame_acl_builder import FrameACLBuilder
from melder.nexus.acl.configurations.frame_acl_command_configuration import (
    FrameACLCommandConfiguration,
)
from melder.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.nexus.acl.frame_acl_configuration_chain import (
    ACLFamilyConfiguration,
    FrameACLConfigurationChain,
)
from melder.nexus.acl.configurations.frame_acl_codegen_configuration import (
    FrameACLCodegenConfiguration,
)
from melder.nexus.acl.validator.frame_acl_validator import FrameACLValidator
from melder.nexus.acl.configurations.frame_acl_view_configuration import (
    FrameACLViewConfiguration,
)
from melder.utilities.helpers.id_builder import IDBuilder
from melder.nexus.acl.configurations.frame_acl_codegen_configuration import (
    FrameACLCodegenConfiguration,
)
from melder.nexus.acl.configurations.frame_acl_command_configuration import (
    FrameACLCommandConfiguration,
)
from melder.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.nexus.acl.configurations.frame_acl_view_configuration import (
    FrameACLViewConfiguration,
)


class FrameACLContainer(Cleanable):
    """

    Purpose:
        Hold all frame-local ACL subsystem objects for one frame in one place.

    Contract:
        - One container exists per frame ACL registration.
        - The container owns separate named version chains for view, command,
          and codegen.
        - Same-name bundle assembly is convenience only; the real storage model
          is separate family chains.
        - The builder is a stable object-singleton inside the container.
        - The container owns validator services used to validate assembled
          snapshots against descriptor truth and cross-child compatibility.

    Registration:
        MELDER KERNEL - guarded. One container per frame ACL registration,
        owned by `FrameACLManager`.

    Subsystem Context:
        The frame-local ACL root. It owns three independent named version
        chains (view, command, codegen), one stable `FrameACLBuilder`
        object-singleton, and the validator services used on assembled
        snapshots.

    System Context:
        The contract's third line records the model correction that matters
        most here: SAME-NAME BUNDLE ASSEMBLY IS CONVENIENCE ONLY - the real
        storage is separate family chains. The three families may legitimately
        hold divergent named contracts, and treating same-name selection as the
        storage model would collapse that freedom.
        The Rift frame-link path chooses NOT to use it, pinning a fixed
        same-name selection per attached frame. Both facts hold at once: storage
        permits divergence, and the Rift attachment path deliberately forgoes it
        so a Rift's effective permissions stay comprehensible.
        Keeping the builder as a stable object-singleton inside the container is
        what enforces the one-draft-at-a-time rule. If callers could construct
        builders freely, concurrent drafts could interleave into a contract
        nobody authored - and because a chain bump fans a refresh out across
        every impacted Rift, that incoherence would propagate.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. FrameACLContainer runtime object. Melder kernel machinery: read it to
        understand the runtime, do not drive it directly.
    """

    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_frame_name",
        "_view_configuration_chains_by_name",
        "_command_configuration_chains_by_name",
        "_codegen_configuration_chains_by_name",
        "_profile_builder",
        "_owns_profile_builder",
        "_change_callback",
        "_frame_acl_validator",
        "_frame_acl_set_compatibility_validator",
        "_frame_acl_builder",
    ]

    def __init__(
            self,
            frame_name: str,
            *,
            history_limit: int = 15,
            profile_builder: Optional[FrameACLProfileBuilder] = None,
            change_callback: Optional[Callable[[str], None]] = None,
    ) -> None:
        """
        Initialize one frame ACL container.

        Args:
            frame_name:
                Stable frame name that owns this ACL container.
            history_limit:
                Maximum number of retained configuration nodes per family chain.
            profile_builder:
                Optional shared ACL profile builder used by the compatibility
                validator.
            change_callback:
                Optional callback invoked after a committed family-chain change
                for this frame.

        Returns:
            None.
        """
        super().__init__()
        if not frame_name:
            raise ValueError("frame_name cannot be empty.")
        if not isinstance(history_limit, int) or history_limit < 1:
            raise ValueError("history_limit must be an integer >= 1.")
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._frame_name: str = frame_name
        self._view_configuration_chains_by_name: Dict[str, FrameACLConfigurationChain] = {}
        self._command_configuration_chains_by_name: Dict[str, FrameACLConfigurationChain] = {}
        self._codegen_configuration_chains_by_name: Dict[str, FrameACLConfigurationChain] = {}
        self._owns_profile_builder: bool = profile_builder is None
        if profile_builder is None:
            profile_builder = FrameACLProfileBuilder()
        self._profile_builder: FrameACLProfileBuilder = profile_builder
        self._frame_acl_validator: FrameACLValidator = FrameACLValidator(
            frame_name,
            self._profile_builder,
        )
        self._change_callback: Optional[Callable[[str], None]] = change_callback
        self._frame_acl_set_compatibility_validator = (
            FrameACLSetCompatibilityValidator(
                frame_name,
                self._profile_builder,
            )
        )
        self._frame_acl_builder: FrameACLBuilder = FrameACLBuilder(self)
        self._seed_default_chains(history_limit=history_limit)

    def cleanup(self) -> None:
        """
        Idempotently cleanup the container and all owned ACL objects.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._frame_acl_builder.cleanup()
            self._frame_acl_validator.cleanup()
            self._frame_acl_set_compatibility_validator.cleanup()
            if self._owns_profile_builder and self._profile_builder is not None:
                self._profile_builder.cleanup()
            for chain in self._view_configuration_chains_by_name.values():
                chain.cleanup()
            for chain in self._command_configuration_chains_by_name.values():
                chain.cleanup()
            for chain in self._codegen_configuration_chains_by_name.values():
                chain.cleanup()
            self._view_configuration_chains_by_name.clear()
            self._command_configuration_chains_by_name.clear()
            self._codegen_configuration_chains_by_name.clear()
            del self._frame_acl_builder
            del self._frame_acl_validator
            del self._frame_acl_set_compatibility_validator
            del self._profile_builder
            del self._owns_profile_builder
            del self._change_callback
            del self._view_configuration_chains_by_name
            del self._command_configuration_chains_by_name
            del self._codegen_configuration_chains_by_name
            del self._frame_name
        del self._lock

    @property
    def frame_name(self) -> str:
        """
        Return the owning frame name.

        Returns:
            str: Owning frame name.
        """
        self.check_cleaned()
        return self._frame_name

    @property
    def frame_acl_builder(self) -> FrameACLBuilder:
        """
        Return the unique builder object for this frame container.

        Returns:
            FrameACLBuilder: Unique builder object.
        """
        self.check_cleaned()
        return self._frame_acl_builder

    @property
    def frame_acl_profile_builder(self) -> FrameACLProfileBuilder:
        """
        Return the shared ACL profile builder/library for this frame container.

        Returns:
            FrameACLProfileBuilder: Shared reusable profile builder.
        """
        self.check_cleaned()
        return self._profile_builder

    @property
    def frame_acl_configuration(self) -> FrameACLConfiguration:
        """
        Return the assembled default ACL configuration snapshot.

        Returns:
            FrameACLConfiguration: Assembled default ACL snapshot.
        """
        self.check_cleaned()
        return self.build_selected_configuration()

    @property
    def named_configurations_by_name(self) -> Dict[str, FrameACLConfiguration]:
        """
        Return assembled same-name ACL snapshots keyed by contract name.

        Returns:
            Dict[str, FrameACLConfiguration]: Assembled same-name ACL snapshots.
        """
        self.check_cleaned()
        with self._lock:
            common_contract_names = (
                set(self._view_configuration_chains_by_name.keys())
                & set(self._command_configuration_chains_by_name.keys())
                & set(self._codegen_configuration_chains_by_name.keys())
            )
        return {
            contract_name: self.get_named_configuration(contract_name)
            for contract_name in sorted(common_contract_names)
        }

    @property
    def frame_acl_validator(self) -> FrameACLValidator:
        """
        Return the frame-scoped ACL validator.

        Returns:
            FrameACLValidator: Frame-scoped validator.
        """
        self.check_cleaned()
        return self._frame_acl_validator

    @property
    def frame_acl_set_compatibility_validator(
            self,
    ) -> FrameACLSetCompatibilityValidator:
        """
        Return the frame-scoped ACL set compatibility validator.

        Returns:
            FrameACLSetCompatibilityValidator:
                Frame-scoped set compatibility validator.
        """
        self.check_cleaned()
        return self._frame_acl_set_compatibility_validator

    @property
    def view_chain_names(self) -> List[str]:
        """
        Return named view-chain registry keys.

        Returns:
            List[str]: Named view-chain keys.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._view_configuration_chains_by_name.keys())

    @property
    def command_chain_names(self) -> List[str]:
        """
        Return named command-chain registry keys.

        Returns:
            List[str]: Named command-chain keys.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._command_configuration_chains_by_name.keys())

    @property
    def codegen_chain_names(self) -> List[str]:
        """
        Return named codegen-chain registry keys.

        Returns:
            List[str]: Named codegen-chain keys.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._codegen_configuration_chains_by_name.keys())

    def get_current_view_configuration(
            self,
            contract_name: str = "default",
    ) -> FrameACLViewConfiguration:
        """
        Return the current selected view configuration for one contract.

        Args:
            contract_name:
                Contract chain name to read the current selection from.

        Returns:
            FrameACLViewConfiguration: Current view configuration.

        Raises:
            RuntimeError: If the chain returns a non-view configuration.
        """
        configuration = self._get_required_family_chain(
            "view",
            contract_name,
        ).get_current_configuration()
        if not isinstance(configuration, FrameACLViewConfiguration):
            raise RuntimeError("View chain returned a non-view configuration.")
        return configuration

    def get_current_command_configuration(
            self,
            contract_name: str = "default",
    ) -> FrameACLCommandConfiguration:
        """
        Return the current selected command configuration for one contract.

        Args:
            contract_name:
                Contract chain name to read the current selection from.

        Returns:
            FrameACLCommandConfiguration: Current command configuration.

        Raises:
            RuntimeError: If the chain returns a non-command configuration.
        """
        configuration = self._get_required_family_chain(
            "command",
            contract_name,
        ).get_current_configuration()
        if not isinstance(configuration, FrameACLCommandConfiguration):
            raise RuntimeError("Command chain returned a non-command configuration.")
        return configuration

    def get_current_codegen_configuration(
            self,
            contract_name: str = "default",
    ) -> FrameACLCodegenConfiguration:
        """
        Return the current selected codegen configuration for one contract.

        Args:
            contract_name:
                Contract chain name to read the current selection from.

        Returns:
            FrameACLCodegenConfiguration: Current codegen configuration.

        Raises:
            RuntimeError: If the chain returns a non-codegen configuration.
        """
        configuration = self._get_required_family_chain(
            "codegen",
            contract_name,
        ).get_current_configuration()
        if not isinstance(configuration, FrameACLCodegenConfiguration):
            raise RuntimeError("Codegen chain returned a non-codegen configuration.")
        return configuration

    def get_named_configuration(
            self,
            contract_name: str = "default",
    ) -> FrameACLConfiguration:
        """
        Return one assembled same-name ACL snapshot for this frame.

        Args:
            contract_name:
                Same-name contract to assemble across all three families.

        Returns:
            FrameACLConfiguration: Assembled ACL snapshot for the selected name.
        """
        self.check_cleaned()
        return self.build_selected_configuration(
            view_contract_name=contract_name,
            command_contract_name=contract_name,
            codegen_contract_name=contract_name,
            reason="named_selection",
        )

    def list_named_configuration_names(self) -> List[str]:
        """
        Return the contract names available across all three families.

        Returns:
            List[str]: Same-name contract keys present in all three registries.
        """
        self.check_cleaned()
        with self._lock:
            return sorted(
                set(self._view_configuration_chains_by_name.keys())
                & set(self._command_configuration_chains_by_name.keys())
                & set(self._codegen_configuration_chains_by_name.keys())
            )

    def register_named_configuration(
            self,
            configuration: FrameACLConfiguration,
            *,
            contract_name: str = "default",
    ) -> FrameACLConfiguration:
        """
        Register one same-name ACL bundle across all three families.

        Args:
            configuration:
                Locked `FrameACLConfiguration` targeting this frame.
            contract_name:
                Contract name to register the bundle under.

        Returns:
            FrameACLConfiguration: Registered assembled bundle snapshot.

        Raises:
            TypeError: If `configuration` is not a FrameACLConfiguration.
            ValueError: If it targets another frame or is not locked.
        """
        self.check_cleaned()
        if not isinstance(configuration, FrameACLConfiguration):
            raise TypeError(
                "configuration must be a FrameACLConfiguration instance."
            )
        if configuration.frame_name != self._frame_name:
            raise ValueError(
                "FrameACLConfiguration targets frame '{0}', expected '{1}'.".format(
                    configuration.frame_name,
                    self._frame_name,
                )
            )
        if not configuration.locked:
            raise ValueError(
                "Named ACL configuration must be locked before registration."
            )
        self._register_family_configuration(
            "view",
            configuration.view_configuration.clone(),
            contract_name=contract_name,
        )
        self._register_family_configuration(
            "command",
            configuration.command_configuration.clone(),
            contract_name=contract_name,
        )
        self._register_family_configuration(
            "codegen",
            configuration.codegen_configuration.clone(),
            contract_name=contract_name,
        )
        self._notify_acl_changed()
        return self.get_named_configuration(contract_name)

    def install_configuration(
            self,
            configuration: FrameACLConfiguration,
            *,
            contract_name: str = "default",
    ) -> FrameACLConfiguration:
        """
        Install one same-name ACL bundle revision across all three families.

        Args:
            configuration:
                Locked `FrameACLConfiguration` targeting this frame.
            contract_name:
                Contract name to install the revision under.

        Returns:
            FrameACLConfiguration: Newly assembled current ACL snapshot.

        Raises:
            TypeError: If `configuration` is not a FrameACLConfiguration.
            ValueError: If it targets another frame or is not locked.
        """
        self.check_cleaned()
        if not isinstance(configuration, FrameACLConfiguration):
            raise TypeError(
                "configuration must be a FrameACLConfiguration instance."
            )
        if configuration.frame_name != self._frame_name:
            raise ValueError(
                "FrameACLConfiguration targets frame '{0}', expected '{1}'.".format(
                    configuration.frame_name,
                    self._frame_name,
                )
            )
        if not configuration.locked:
            raise ValueError("Configuration must be locked before installation.")
        self.insert_head_view_configuration(
            configuration.view_configuration.clone(),
            contract_name=contract_name,
            select_as_current=True,
        )
        self.insert_head_command_configuration(
            configuration.command_configuration.clone(),
            contract_name=contract_name,
            select_as_current=True,
        )
        self.insert_head_codegen_configuration(
            configuration.codegen_configuration.clone(),
            contract_name=contract_name,
            select_as_current=True,
        )
        self._notify_acl_changed()
        return self.get_named_configuration(contract_name)

    def create_new_from_view_configuration(
            self,
            configuration_id: str,
            *,
            contract_name: str = "default",
            reason: str,
    ) -> FrameACLViewConfiguration:
        """
        Create a new view draft copied from one existing view revision.

        Args:
            configuration_id:
                Source view revision id to copy.
            contract_name:
                Contract chain the source revision lives in.
            reason:
                Audit reason recorded on the new draft.

        Returns:
            FrameACLViewConfiguration: New unlocked view configuration draft.

        Raises:
            RuntimeError: If the chain returns a non-view configuration.
        """
        configuration = self._get_required_family_chain(
            "view",
            contract_name,
        ).create_new_from_acl_configuration(
            configuration_id,
            reason=reason,
        )
        if not isinstance(configuration, FrameACLViewConfiguration):
            raise RuntimeError("View chain returned a non-view configuration.")
        return configuration

    def create_new_from_command_configuration(
            self,
            configuration_id: str,
            *,
            contract_name: str = "default",
            reason: str,
    ) -> FrameACLCommandConfiguration:
        """
        Create a new command draft copied from one existing command revision.

        Args:
            configuration_id:
                Source command revision id to copy.
            contract_name:
                Contract chain the source revision lives in.
            reason:
                Audit reason recorded on the new draft.

        Returns:
            FrameACLCommandConfiguration: New unlocked command configuration draft.

        Raises:
            RuntimeError: If the chain returns a non-command configuration.
        """
        configuration = self._get_required_family_chain(
            "command",
            contract_name,
        ).create_new_from_acl_configuration(
            configuration_id,
            reason=reason,
        )
        if not isinstance(configuration, FrameACLCommandConfiguration):
            raise RuntimeError("Command chain returned a non-command configuration.")
        return configuration

    def create_new_from_codegen_configuration(
            self,
            configuration_id: str,
            *,
            contract_name: str = "default",
            reason: str,
    ) -> FrameACLCodegenConfiguration:
        """
        Create a new codegen draft copied from one existing codegen revision.

        Args:
            configuration_id:
                Source codegen revision id to copy.
            contract_name:
                Contract chain the source revision lives in.
            reason:
                Audit reason recorded on the new draft.

        Returns:
            FrameACLCodegenConfiguration: New unlocked codegen configuration draft.

        Raises:
            RuntimeError: If the chain returns a non-codegen configuration.
        """
        configuration = self._get_required_family_chain(
            "codegen",
            contract_name,
        ).create_new_from_acl_configuration(
            configuration_id,
            reason=reason,
        )
        if not isinstance(configuration, FrameACLCodegenConfiguration):
            raise RuntimeError("Codegen chain returned a non-codegen configuration.")
        return configuration

    def insert_head_view_configuration(
            self,
            configuration: FrameACLViewConfiguration,
            *,
            contract_name: str = "default",
            select_as_current: bool,
    ) -> FrameACLViewConfiguration:
        """
        Insert one view configuration revision at the head of a named chain.

        Args:
            configuration:
                View configuration revision to insert at the head.
            contract_name:
                Named chain to insert into.
            select_as_current:
                When True, select the inserted revision as current.

        Returns:
            FrameACLViewConfiguration: Inserted view configuration revision.

        Raises:
            RuntimeError: If the chain returns a non-view configuration.
        """
        self._validate_family_change(
            family_name="view",
            contract_name=contract_name,
            next_view_configuration=configuration,
        )
        chain = self._get_required_family_chain("view", contract_name)
        inserted = chain.insert_head_configuration(
            configuration,
            select_as_current=select_as_current,
        )
        self._notify_acl_changed()
        if not isinstance(inserted, FrameACLViewConfiguration):
            raise RuntimeError("View chain returned a non-view configuration.")
        return inserted

    def insert_head_command_configuration(
            self,
            configuration: FrameACLCommandConfiguration,
            *,
            contract_name: str = "default",
            select_as_current: bool,
    ) -> FrameACLCommandConfiguration:
        """
        Insert one command configuration revision at the head of a named chain.

        Args:
            configuration:
                Command configuration revision to insert at the head.
            contract_name:
                Named chain to insert into.
            select_as_current:
                When True, select the inserted revision as current.

        Returns:
            FrameACLCommandConfiguration: Inserted command configuration revision.

        Raises:
            RuntimeError: If the chain returns a non-command configuration.
        """
        self._validate_family_change(
            family_name="command",
            contract_name=contract_name,
            next_command_configuration=configuration,
        )
        chain = self._get_required_family_chain("command", contract_name)
        inserted = chain.insert_head_configuration(
            configuration,
            select_as_current=select_as_current,
        )
        self._notify_acl_changed()
        if not isinstance(inserted, FrameACLCommandConfiguration):
            raise RuntimeError("Command chain returned a non-command configuration.")
        return inserted

    def insert_head_codegen_configuration(
            self,
            configuration: FrameACLCodegenConfiguration,
            *,
            contract_name: str = "default",
            select_as_current: bool,
    ) -> FrameACLCodegenConfiguration:
        """
        Insert one codegen configuration revision at the head of a named chain.

        Args:
            configuration:
                Codegen configuration revision to insert at the head.
            contract_name:
                Named chain to insert into.
            select_as_current:
                When True, select the inserted revision as current.

        Returns:
            FrameACLCodegenConfiguration: Inserted codegen configuration revision.

        Raises:
            RuntimeError: If the chain returns a non-codegen configuration.
        """
        self._validate_family_change(
            family_name="codegen",
            contract_name=contract_name,
            next_codegen_configuration=configuration,
        )
        chain = self._get_required_family_chain("codegen", contract_name)
        inserted = chain.insert_head_configuration(
            configuration,
            select_as_current=select_as_current,
        )
        self._notify_acl_changed()
        if not isinstance(inserted, FrameACLCodegenConfiguration):
            raise RuntimeError("Codegen chain returned a non-codegen configuration.")
        return inserted

    def select_current_view_configuration(
            self,
            configuration_id: str,
            *,
            contract_name: str = "default",
    ) -> FrameACLViewConfiguration:
        """
        Select one existing view configuration revision as current.

        Args:
            configuration_id:
                Existing view revision id to select.
            contract_name:
                Named chain the revision lives in.

        Returns:
            FrameACLViewConfiguration: Newly selected current view revision.

        Raises:
            RuntimeError: If the chain returns a non-view configuration.
        """
        selected = self._get_required_family_chain(
            "view",
            contract_name,
        ).select_current_configuration(configuration_id)
        self._notify_acl_changed()
        if not isinstance(selected, FrameACLViewConfiguration):
            raise RuntimeError("View chain returned a non-view configuration.")
        return selected

    def select_current_command_configuration(
            self,
            configuration_id: str,
            *,
            contract_name: str = "default",
    ) -> FrameACLCommandConfiguration:
        """
        Select one existing command configuration revision as current.

        Args:
            configuration_id:
                Existing command revision id to select.
            contract_name:
                Named chain the revision lives in.

        Returns:
            FrameACLCommandConfiguration: Newly selected current command revision.

        Raises:
            RuntimeError: If the chain returns a non-command configuration.
        """
        selected = self._get_required_family_chain(
            "command",
            contract_name,
        ).select_current_configuration(configuration_id)
        self._notify_acl_changed()
        if not isinstance(selected, FrameACLCommandConfiguration):
            raise RuntimeError("Command chain returned a non-command configuration.")
        return selected

    def select_current_codegen_configuration(
            self,
            configuration_id: str,
            *,
            contract_name: str = "default",
    ) -> FrameACLCodegenConfiguration:
        """
        Select one existing codegen configuration revision as current.

        Args:
            configuration_id:
                Existing codegen revision id to select.
            contract_name:
                Named chain the revision lives in.

        Returns:
            FrameACLCodegenConfiguration: Newly selected current codegen revision.

        Raises:
            RuntimeError: If the chain returns a non-codegen configuration.
        """
        selected = self._get_required_family_chain(
            "codegen",
            contract_name,
        ).select_current_configuration(configuration_id)
        self._notify_acl_changed()
        if not isinstance(selected, FrameACLCodegenConfiguration):
            raise RuntimeError("Codegen chain returned a non-codegen configuration.")
        return selected

    def rollback_view_configuration(
            self,
            configuration_id: str,
            *,
            contract_name: str = "default",
    ) -> FrameACLViewConfiguration:
        """
        Roll current view selection back to one historical revision.

        Args:
            configuration_id:
                Historical view revision id to roll back to.
            contract_name:
                Named chain the revision lives in.

        Returns:
            FrameACLViewConfiguration: Newly selected current view revision.

        Raises:
            RuntimeError: If the chain returns a non-view configuration.
        """
        rolled_back = self._get_required_family_chain(
            "view",
            contract_name,
        ).rollback_to_configuration(configuration_id)
        self._notify_acl_changed()
        if not isinstance(rolled_back, FrameACLViewConfiguration):
            raise RuntimeError("View chain returned a non-view configuration.")
        return rolled_back

    def rollback_command_configuration(
            self,
            configuration_id: str,
            *,
            contract_name: str = "default",
    ) -> FrameACLCommandConfiguration:
        """
        Roll current command selection back to one historical revision.

        Args:
            configuration_id:
                Historical command revision id to roll back to.
            contract_name:
                Named chain the revision lives in.

        Returns:
            FrameACLCommandConfiguration: Newly selected current command revision.

        Raises:
            RuntimeError: If the chain returns a non-command configuration.
        """
        rolled_back = self._get_required_family_chain(
            "command",
            contract_name,
        ).rollback_to_configuration(configuration_id)
        self._notify_acl_changed()
        if not isinstance(rolled_back, FrameACLCommandConfiguration):
            raise RuntimeError("Command chain returned a non-command configuration.")
        return rolled_back

    def rollback_codegen_configuration(
            self,
            configuration_id: str,
            *,
            contract_name: str = "default",
    ) -> FrameACLCodegenConfiguration:
        """
        Roll current codegen selection back to one historical revision.

        Args:
            configuration_id:
                Historical codegen revision id to roll back to.
            contract_name:
                Named chain the revision lives in.

        Returns:
            FrameACLCodegenConfiguration: Newly selected current codegen revision.

        Raises:
            RuntimeError: If the chain returns a non-codegen configuration.
        """
        rolled_back = self._get_required_family_chain(
            "codegen",
            contract_name,
        ).rollback_to_configuration(configuration_id)
        self._notify_acl_changed()
        if not isinstance(rolled_back, FrameACLCodegenConfiguration):
            raise RuntimeError("Codegen chain returned a non-codegen configuration.")
        return rolled_back

    def list_view_configurations(
            self,
            *,
            contract_name: str = "default",
            limit: Optional[int] = None,
    ) -> List[FrameACLViewConfiguration]:
        """
        Return view revisions for one named chain from newest to oldest.

        Args:
            contract_name:
                Named chain to list revisions from.
            limit:
                Optional max number of revisions to return (newest first).

        Returns:
            List[FrameACLViewConfiguration]: View configuration revisions.

        Raises:
            RuntimeError: If the chain returns a non-view configuration.
        """
        raw_configurations = self._get_required_family_chain(
            "view",
            contract_name,
        ).list_configurations(limit=limit)
        configurations: List[FrameACLViewConfiguration] = []
        for configuration in raw_configurations:
            if not isinstance(configuration, FrameACLViewConfiguration):
                raise RuntimeError("View chain returned a non-view configuration.")
            configurations.append(configuration)
        return configurations

    def list_command_configurations(
            self,
            *,
            contract_name: str = "default",
            limit: Optional[int] = None,
    ) -> List[FrameACLCommandConfiguration]:
        """
        Return command revisions for one named chain from newest to oldest.

        Args:
            contract_name:
                Named chain to list revisions from.
            limit:
                Optional max number of revisions to return (newest first).

        Returns:
            List[FrameACLCommandConfiguration]: Command configuration revisions.

        Raises:
            RuntimeError: If the chain returns a non-command configuration.
        """
        raw_configurations = self._get_required_family_chain(
            "command",
            contract_name,
        ).list_configurations(limit=limit)
        configurations: List[FrameACLCommandConfiguration] = []
        for configuration in raw_configurations:
            if not isinstance(configuration, FrameACLCommandConfiguration):
                raise RuntimeError("Command chain returned a non-command configuration.")
            configurations.append(configuration)
        return configurations

    def list_codegen_configurations(
            self,
            *,
            contract_name: str = "default",
            limit: Optional[int] = None,
    ) -> List[FrameACLCodegenConfiguration]:
        """
        Return codegen revisions for one named chain from newest to oldest.

        Args:
            contract_name:
                Named chain to list revisions from.
            limit:
                Optional max number of revisions to return (newest first).

        Returns:
            List[FrameACLCodegenConfiguration]: Codegen configuration revisions.

        Raises:
            RuntimeError: If the chain returns a non-codegen configuration.
        """
        raw_configurations = self._get_required_family_chain(
            "codegen",
            contract_name,
        ).list_configurations(limit=limit)
        configurations: List[FrameACLCodegenConfiguration] = []
        for configuration in raw_configurations:
            if not isinstance(configuration, FrameACLCodegenConfiguration):
                raise RuntimeError("Codegen chain returned a non-codegen configuration.")
            configurations.append(configuration)
        return configurations

    def build_selected_configuration(
            self,
            *,
            view_contract_name: str = "default",
            command_contract_name: str = "default",
            codegen_contract_name: str = "default",
            reason: str = "assembled_selection",
    ) -> FrameACLConfiguration:
        """
        Assemble one full ACL snapshot from selected family chains.

        Args:
            view_contract_name:
                Contract chain to read the current view configuration from.
            command_contract_name:
                Contract chain to read the current command configuration from.
            codegen_contract_name:
                Contract chain to read the current codegen configuration from.
            reason:
                Audit reason recorded on the assembled snapshot.

        Returns:
            FrameACLConfiguration: Detached assembled ACL snapshot (locked).
        """
        self.check_cleaned()
        view_configuration = self.get_current_view_configuration(view_contract_name)
        command_configuration = self.get_current_command_configuration(
            command_contract_name
        )
        codegen_configuration = self.get_current_codegen_configuration(
            codegen_contract_name
        )
        configuration_id = self._make_assembled_configuration_id(
            view_configuration.configuration_id,
            command_configuration.configuration_id,
            codegen_configuration.configuration_id,
        )
        return FrameACLConfiguration.create_from_selected_configurations(
            frame_name=self._frame_name,
            view_configuration=view_configuration,
            command_configuration=command_configuration,
            codegen_configuration=codegen_configuration,
            reason=reason,
            locked=True,
            configuration_id=configuration_id,
        )

    def _seed_default_chains(self, *, history_limit: int) -> None:
        """
        Seed the reserved default chains for all three config families.

        Args:
            history_limit:
                Maximum retained revision count per family chain.

        Returns:
            None.
        """
        self._view_configuration_chains_by_name["default"] = (
            FrameACLConfigurationChain(
                family_name="view",
                contract_name="default",
                default_configuration=FrameACLViewConfiguration.from_profile(
                    self._profile_builder.get_required_view_profile("safe"),
                    reason="default",
                    locked=True,
                ),
                history_limit=history_limit,
            )
        )
        self._command_configuration_chains_by_name["default"] = (
            FrameACLConfigurationChain(
                family_name="command",
                contract_name="default",
                default_configuration=FrameACLCommandConfiguration.create_default(
                    reason="default",
                    locked=True,
                ),
                history_limit=history_limit,
            )
        )
        self._codegen_configuration_chains_by_name["default"] = (
            FrameACLConfigurationChain(
                family_name="codegen",
                contract_name="default",
                default_configuration=FrameACLCodegenConfiguration.from_profile(
                    self._profile_builder.get_required_codegen_profile("safe"),
                    reason="default",
                    locked=True,
                ),
                history_limit=history_limit,
            )
        )

    def _validate_family_change(
            self,
            *,
            family_name: str,
            contract_name: str,
            next_view_configuration: Optional[FrameACLViewConfiguration] = None,
            next_command_configuration: Optional[FrameACLCommandConfiguration] = None,
            next_codegen_configuration: Optional[FrameACLCodegenConfiguration] = None,
    ) -> None:
        """
        Validate one family change by assembling a same-name snapshot.

        Args:
            family_name:
                Target family being changed.
            contract_name:
                Target contract name.
            next_view_configuration:
                Optional replacement view configuration.
            next_command_configuration:
                Optional replacement command configuration.
            next_codegen_configuration:
                Optional replacement codegen configuration.

        Returns:
            None.
        """
        try:
            current_view = (
                next_view_configuration
                if next_view_configuration is not None
                else self.get_current_view_configuration(contract_name)
            )
        except KeyError:
            current_view = self.get_current_view_configuration()
        try:
            current_command = (
                next_command_configuration
                if next_command_configuration is not None
                else self.get_current_command_configuration(contract_name)
            )
        except KeyError:
            current_command = self.get_current_command_configuration()
        try:
            current_codegen = (
                next_codegen_configuration
                if next_codegen_configuration is not None
                else self.get_current_codegen_configuration(contract_name)
            )
        except KeyError:
            current_codegen = self.get_current_codegen_configuration()

        assembled_configuration = FrameACLConfiguration.create_from_selected_configurations(
            frame_name=self._frame_name,
            view_configuration=current_view,
            command_configuration=current_command,
            codegen_configuration=current_codegen,
            reason="family_validation_{0}".format(family_name),
            locked=True,
        )
        try:
            self._frame_acl_validator.validate_configuration(assembled_configuration)
            self._frame_acl_set_compatibility_validator.validate_configuration(
                assembled_configuration
            )
        finally:
            assembled_configuration.cleanup()

    def _register_family_configuration(
            self,
            family_name: str,
            configuration: ACLFamilyConfiguration,
            *,
            contract_name: str,
    ) -> ACLFamilyConfiguration:
        """
        Register one new named chain seeded from a locked family configuration.

        Args:
            family_name:
                ACL family name.
            configuration:
                Locked family configuration revision.
            contract_name:
                Named contract to seed.

        Returns:
            object: Registered configuration revision.
        """
        if not contract_name:
            raise ValueError("contract_name cannot be empty.")
        if not hasattr(configuration, "locked") or not configuration.locked:
            raise ValueError(
                "Named ACL family configuration must be locked before registration."
            )
        registry = self._get_family_registry(family_name)
        with self._lock:
            if contract_name in registry:
                raise ValueError(
                    "ACL {0} contract '{1}' already exists for frame '{2}'.".format(
                        family_name,
                        contract_name,
                        self._frame_name,
                    )
                )
            registry[contract_name] = FrameACLConfigurationChain(
                family_name=family_name,
                contract_name=contract_name,
                default_configuration=configuration,
                history_limit=registry["default"].history_limit,
            )
            return configuration

    def _get_family_registry(
            self,
            family_name: str,
    ) -> Dict[str, FrameACLConfigurationChain]:
        """
        Return the named-chain registry for one ACL family.

        Args:
            family_name:
                ACL family name.

        Returns:
            Dict[str, FrameACLConfigurationChain]: Family chain registry.
        """
        self.check_cleaned()
        if family_name == "view":
            return self._view_configuration_chains_by_name
        if family_name == "command":
            return self._command_configuration_chains_by_name
        if family_name == "codegen":
            return self._codegen_configuration_chains_by_name
        raise ValueError("Unknown ACL family '{0}'.".format(family_name))

    def _get_required_family_chain(
            self,
            family_name: str,
            contract_name: str,
    ) -> FrameACLConfigurationChain:
        """
        Return one required family chain or raise.

        Args:
            family_name:
                ACL family name.
            contract_name:
                Named contract inside that family.

        Returns:
            FrameACLConfigurationChain: Required family chain.
        """
        if not contract_name:
            raise ValueError("contract_name cannot be empty.")
        registry = self._get_family_registry(family_name)
        with self._lock:
            try:
                return registry[contract_name]
            except KeyError as exc:
                raise KeyError(
                    "No ACL {0} contract named '{1}' is registered for frame '{2}'.".format(
                        family_name,
                        contract_name,
                        self._frame_name,
                    )
                ) from exc

    @staticmethod
    def _make_assembled_configuration_id(
            view_configuration_id: str,
            command_configuration_id: str,
            codegen_configuration_id: str,
    ) -> str:
        """
        Build the stable assembled bundle id from selected child revision ids.

        Args:
            view_configuration_id:
                Selected view revision id.
            command_configuration_id:
                Selected command revision id.
            codegen_configuration_id:
                Selected codegen revision id.

        Returns:
            str: Stable assembled configuration id.
        """
        return "view:{0}|command:{1}|codegen:{2}".format(
            view_configuration_id,
            command_configuration_id,
            codegen_configuration_id,
        )

    def _notify_acl_changed(self) -> None:
        """
        Notify the owning manager/Nexus that this frame ACL state changed.

        Returns:
            None.
        """
        if self._change_callback is not None:
            self._change_callback(self._frame_name)
