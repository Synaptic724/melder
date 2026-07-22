from abc import ABC, abstractmethod
from typing import Any


class CodegenCreationFamilyStep(ABC):
    """
    Shared internal step contract for codegen-creation families.

    Purpose:
        Give family strategies one uniform internal shape for ordered build
        steps without widening the public `SpellCodegenStrategy` facade.

    Contract:
        - Steps mutate only the supplied family-local state object.
        - Steps do not own discovery or outer facade selection.
        - The family strategy controls step ordering.
    """

    __slots__ = ()

    @property
    @abstractmethod
    def step_id(self) -> str:
        """
        Return the stable internal step id.

        Returns:
            str: Identifier used to order and track this step within its family.
        """
        raise NotImplementedError

    @abstractmethod
    def apply(
            self,
            state: Any,
    ) -> None:
        """
        Mutate the supplied family-local state object.

        Contract:
            Reads and mutates ONLY the passed `state` (the family-local build
            accumulator); owns neither discovery nor facade selection, and does
            not control its own ordering - the family strategy sequences steps.

        Args:
            state:
                Family-local state object this step advances in place.

        Returns:
            None.
        """
        raise NotImplementedError
