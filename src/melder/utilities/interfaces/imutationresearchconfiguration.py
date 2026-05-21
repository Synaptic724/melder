from typing import Protocol, runtime_checkable

from melder.utilities.interfaces.icleanable import ICleanable


@runtime_checkable
class IMutationResearchConfiguration(ICleanable, Protocol):
    """
    Structural contract for mutation-research root configuration.
    """

    @property
    def frozen(self) -> bool:
        ...

    @property
    def activated(self) -> bool:
        ...

    def with_defaults(self) -> "IMutationResearchConfiguration":
        ...

    def with_unrestricted_module_mutations(
            self,
            enabled: bool,
    ) -> "IMutationResearchConfiguration":
        ...

    def freeze(self) -> None:
        ...

    def finalize(self) -> "IMutationResearchConfiguration":
        ...

    def activate(self) -> "IMutationResearchConfiguration":
        ...

