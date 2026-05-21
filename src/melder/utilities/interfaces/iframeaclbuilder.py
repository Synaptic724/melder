from typing import Optional, Protocol, Union, runtime_checkable
from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.iframeaclcodegenbuilder import IFrameACLCodegenBuilder
from melder.utilities.interfaces.iframeaclcodegenconfiguration import IFrameACLCodegenConfiguration
from melder.utilities.interfaces.iframeaclcommandbuilder import IFrameACLCommandBuilder
from melder.utilities.interfaces.iframeaclcommandconfiguration import IFrameACLCommandConfiguration
from melder.utilities.interfaces.iframeaclviewbuilder import IFrameACLViewBuilder
from melder.utilities.interfaces.iframeaclviewconfiguration import IFrameACLViewConfiguration

@runtime_checkable
class IFrameACLBuilder(ICleanable, Protocol):
    """
    Frame-local ACL builder contract used by the family-specific builders.

    Contract:
        - Owns at most one active family draft at a time.
        - Exposes generic profile, precision, commit, and discard operations.
        - Exposes typed accessors for the currently active family draft.
    """

    @property
    def change_active(self) -> bool:
        """
        Return whether the builder currently owns one open change session.

        Returns:
            bool: True when a change session is active.
        """
        ...

    @property
    def draft_family_name(self) -> Optional[str]:
        """
        Return the ACL family currently targeted by the active draft session.

        Returns:
            Optional[str]: Draft family name when one exists.
        """
        ...

    @property
    def draft_contract_name(self) -> Optional[str]:
        """
        Return the contract name currently targeted by the active draft session.

        Returns:
            Optional[str]: Draft contract name when one exists.
        """
        ...

    def begin_view_change(
            self,
            *,
            contract_name: str = "default",
            reason: str = "builder_draft",
    ) -> IFrameACLViewBuilder:
        """
        Start one view draft session and return the fluent view builder.

        Returns:
            IFrameACLViewBuilder: Fluent builder over the active view draft.
        """
        ...

    def begin_command_change(
            self,
            *,
            contract_name: str = "default",
            reason: str = "builder_draft",
    ) -> IFrameACLCommandBuilder:
        """
        Start one command draft session and return the fluent command builder.

        Returns:
            IFrameACLCommandBuilder: Fluent builder over the active command
            draft.
        """
        ...

    def begin_codegen_change(
            self,
            *,
            contract_name: str = "default",
            reason: str = "builder_draft",
    ) -> IFrameACLCodegenBuilder:
        """
        Start one codegen draft session and return the fluent codegen builder.

        Returns:
            IFrameACLCodegenBuilder: Fluent builder over the active codegen
            draft.
        """
        ...

    def set_profile_name(self, profile_name: str) -> None:
        """
        Replace the base profile on the active family draft.

        Returns:
            None.
        """
        ...

    def set_precision_profile_name(
            self,
            profile_name: Optional[str],
    ) -> None:
        """
        Replace or clear the precision profile on the active family draft.

        Returns:
            None.
        """
        ...

    def commit_change(
            self,
    ) -> Union[
        IFrameACLViewConfiguration,
        IFrameACLCommandConfiguration,
        IFrameACLCodegenConfiguration,
    ]:
        """
        Finalize and install the active family draft.

        Returns:
            Union[IFrameACLViewConfiguration, IFrameACLCommandConfiguration, IFrameACLCodegenConfiguration]:
                Newly installed family configuration.
        """
        ...

    def discard_change(self) -> None:
        """
        Discard the active family draft.

        Returns:
            None.
        """
        ...

    def _require_active_view_configuration(self) -> IFrameACLViewConfiguration:
        """
        Return the active view draft or raise.

        Returns:
            IFrameACLViewConfiguration: Active view draft.
        """
        ...

    def _require_active_command_configuration(self) -> IFrameACLCommandConfiguration:
        """
        Return the active command draft or raise.

        Returns:
            IFrameACLCommandConfiguration: Active command draft.
        """
        ...

    def _require_active_codegen_configuration(self) -> IFrameACLCodegenConfiguration:
        """
        Return the active codegen draft or raise.

        Returns:
            IFrameACLCodegenConfiguration: Active codegen draft.
        """
        ...
