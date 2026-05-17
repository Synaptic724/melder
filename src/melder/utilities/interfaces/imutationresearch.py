from typing import Dict, List, Optional, Protocol, Sequence, runtime_checkable

from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.imutationconduit import IMutationConduit
from melder.utilities.interfaces.imutationframe import IMutationFrame
from melder.utilities.interfaces.imutationresearchconfiguration import (
    IMutationResearchConfiguration,
)
from melder.utilities.interfaces.imutationresearchconfigurationbuilder import (
    IMutationResearchConfigurationBuilder,
)


@runtime_checkable
class IMutationResearch(ICleanable, Protocol):
    """
    Structural contract for the Aether-owned MutationResearch root.
    """

    @property
    def configured(self) -> bool:
        ...

    @property
    def is_configured(self) -> bool:
        ...

    @property
    def activated(self) -> bool:
        ...

    @property
    def is_activated(self) -> bool:
        ...

    @property
    def configuration(self) -> Optional["IMutationResearchConfiguration"]:
        ...

    def create_configuration(self) -> "IMutationResearchConfiguration":
        ...

    def create_configuration_builder(self) -> "IMutationResearchConfigurationBuilder":
        ...

    def configure(
            self,
            configuration: "IMutationResearchConfiguration",
    ) -> None:
        ...

    def activate(
            self,
            configuration: Optional["IMutationResearchConfiguration"] = None,
    ) -> None:
        ...

    def deactivate(self) -> None:
        ...

    def create_mutation_conduit(self, conduit) -> "IMutationConduit":
        ...

    def create_mutation_frame(
            self,
            aetheric_frame_name: str = "default",
    ) -> "IMutationFrame":
        ...

    def create_session(
            self,
            target_index,
            *,
            name: Optional[str] = None,
            level: Optional[int] = None,
            metadata: Optional[Dict[str, object]] = None,
    ):
        ...

    def get_session_for_index(self, target_index) -> Optional[object]:
        ...

    def get_session_by_index_id(self, index_id: str) -> Optional[object]:
        ...

    def list_sessions(self) -> Sequence[object]:
        ...

    def remove_session_for_index(self, target_index) -> None:
        ...

    def begin_spell_mutation(
            self,
            target_index,
            *,
            research_name: Optional[str] = None,
            message: Optional[str] = None,
            tags: Optional[List[str]] = None,
    ):
        ...

    def begin_creation_mutation(
            self,
            target_index,
            creation_id: str,
            *,
            research_name: Optional[str] = None,
            message: Optional[str] = None,
            tags: Optional[List[str]] = None,
    ):
        ...
