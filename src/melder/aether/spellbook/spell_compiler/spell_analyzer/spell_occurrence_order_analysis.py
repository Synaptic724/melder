from typing import List

from melder.utilities.general_base.cleanable import Cleanable


class SpellOccurrenceOrderAnalysis(Cleanable):
    """
    Occurrence-order analysis artifact.

    Purpose:
        Hold only execution-order decisions derived from the occurrence graph.
    """

    __slots__ = Cleanable.__slots__ + [
        "execution_order",
        "execution_order_count",
    ]

    def __init__(
            self,
            *,
            execution_order: List[str],
    ) -> None:
        """
        Build one occurrence-order analysis artifact.
        """
        super().__init__()
        self.execution_order = execution_order
        self.execution_order_count = len(execution_order)

    def cleanup(self) -> None:
        """
        Deterministically release owned order-analysis data.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self.execution_order.clear()
        del self.execution_order
        del self.execution_order_count
