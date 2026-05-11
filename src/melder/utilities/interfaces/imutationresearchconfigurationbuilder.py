from typing import Protocol, runtime_checkable

from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.imutationresearchconfiguration import (
    IMutationResearchConfiguration,
)


@runtime_checkable
class IMutationResearchConfigurationBuilder(ICleanable, Protocol):
    """
    Structural contract for the one-shot mutation-research configuration builder.
    """

    def with_defaults(self) -> "IMutationResearchConfigurationBuilder":
        ...

    def with_unrestricted_module_mutations(
            self,
            enabled: bool,
    ) -> "IMutationResearchConfigurationBuilder":
        ...

    def build(self) -> IMutationResearchConfiguration:
        ...

    def finalize(self) -> IMutationResearchConfiguration:
        ...

    def activate(self) -> IMutationResearchConfiguration:
        ...
