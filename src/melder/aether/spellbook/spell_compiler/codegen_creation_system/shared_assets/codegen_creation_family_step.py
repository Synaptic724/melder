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
        """
        raise NotImplementedError

    @abstractmethod
    def apply(
            self,
            state: Any,
    ) -> None:
        """
        Mutate the supplied family-local state object.
        """
        raise NotImplementedError
