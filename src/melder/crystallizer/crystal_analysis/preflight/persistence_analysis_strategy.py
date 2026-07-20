
from abc import ABC, abstractmethod
from typing import ClassVar, Dict, List

from melder.__melder_registration_guard__ import (
    __melder_registration_guard__ as _mrg,
)


class PersistenceAnalysisStrategy(ABC):
    """
    One analysis pass over a persistence payload bundle.

    Purpose:
        The persistence analyzer (owner charter) pre-flights bootload
        problems BEFORE a user trusts a formation or checkpoint: each
        strategy inspects one concern (link integrity, contract peers,
        hydration viability, configuration loss) and reports findings.

    Contract:
        - Explicit runtime inheritance contract (the sanctioned ABC
          case: multiple concrete implementations share this surface and
          the analyzer iterates them polymorphically).
        - Strategies are STATELESS analyzers: `analyze` reads the bundle
          and returns findings; it never mutates the bundle and never
          touches live runtime objects.
        - Finding row shape (every strategy, every row):
          {"strategy": str, "severity": "blocker"|"warning"|"info",
           "kind": str, "key": str, "detail": str}.
          Severity semantics: "blocker" = the restore will FAIL or
          structurally omit the anchor; "warning" = the restore completes
          but shortfalls this element; "info" = honest context the user
          should know (code participation, lossy values).

    Threading:
        Stateless by contract; safe to share.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. One analysis pass over a persistence payload bundle. Melder kernel "
        "machinery: read it to understand the runtime, do not drive it directly."
    )

    __melder_internal__: ClassVar[object] = _mrg.sentinel

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Return the strategy's stable report name.

        Returns:
            str: Snake-case identifier used in finding rows.
        """
        raise NotImplementedError

    @abstractmethod
    def analyze(
            self,
            payload_bundle: Dict[str, Dict[str, Dict[str, object]]],
    ) -> List[Dict[str, object]]:
        """
        Analyze one payload bundle and return finding rows.

        Args:
            payload_bundle:
                {kind: {key: payload}} - a formation's payload slice or
                a checkpoint's captured payloads (both share the twin
                describe() shapes).

        Returns:
            List[Dict[str, object]]:
                Finding rows per the class contract (empty = clean for
                this concern).

        Raises:
            NotImplementedError: On the abstract base.
        """
        raise NotImplementedError
