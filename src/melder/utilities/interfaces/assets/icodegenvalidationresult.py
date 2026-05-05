from typing import Dict, Optional, Protocol, Tuple, runtime_checkable
from melder.utilities.interfaces.assets.icleanable import ICleanable

@runtime_checkable
class ICodegenValidationResult(ICleanable, Protocol):
    """
    Interface for the validator-owned codegen result type.
    """

    @property
    def accepted(self) -> bool:
        """
        Return the validation acceptance state.
        """
        ...

    @property
    def frame_name(self) -> str:
        """
        Return the target frame name.
        """
        ...

    @property
    def reason(self) -> Optional[str]:
        """
        Return the optional validation reason.
        """
        ...

    @property
    def validation_issues(self) -> Tuple[str, ...]:
        """
        Return the validation issues tuple.
        """
        ...

    @property
    def transaction_id(self) -> Optional[str]:
        """
        Return the optional transaction id.
        """
        ...

    def to_payload(self) -> Dict[str, object]:
        """
        Return the public validation payload.
        """
        ...
