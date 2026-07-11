
from typing import ClassVar, Dict, List

from melder.__melder_registration_guard__ import (
    __melder_registration_guard__ as _mrg,
)
from melder.crystallizer.crystal_analysis.preflight.persistence_analysis_strategy import (
    PersistenceAnalysisStrategy,
)


class ConfigurationLossStrategy(PersistenceAnalysisStrategy):
    """
    Surface configuration facts a record can never fully rebuild.

    Purpose:
        Callable-bearing configuration never round-trips (record law:
        presence flags only). This pass tells the user WHICH code
        participation their bootloader must re-supply: spellbook hooks
        and the aether root's resolver/default-logger flags.

    Contract:
        - Severity "info": these are honest expectations, not failures -
          the restore reports them as shortfalls and continues.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel

    @property
    def name(self) -> str:
        """
        Return the strategy's stable report name.

        Returns:
            str: "configuration_loss".
        """
        return "configuration_loss"

    def analyze(
            self,
            payload_bundle: Dict[str, Dict[str, Dict[str, object]]],
    ) -> List[Dict[str, object]]:
        """
        Report every code-participation expectation in the bundle.

        Args:
            payload_bundle:
                {kind: {key: payload}} bundle under analysis.

        Returns:
            List[Dict[str, object]]: Info rows per hook/callable flag.
        """
        findings: List[Dict[str, object]] = []
        for spellbook_id, payload in dict(
                payload_bundle.get("spellbook", {})
        ).items():
            for hook_name in list(payload.get("hook_names", [])):
                findings.append({
                    "strategy": self.name,
                    "severity": "info",
                    "kind": "spellbook",
                    "key": spellbook_id,
                    "detail": (
                        "hook {0!r} needs code participation at "
                        "bootload; the record carries its name "
                        "only".format(str(hook_name))
                    ),
                })
        for key, payload in dict(payload_bundle.get("aether", {})).items():
            configuration = dict(payload.get("configuration_payload", {}))
            for flag_name in (
                    "channel_logger_resolver_present",
                    "default_logger_present",
            ):
                if bool(configuration.get(flag_name)):
                    findings.append({
                        "strategy": self.name,
                        "severity": "info",
                        "kind": "aether",
                        "key": key,
                        "detail": (
                            "{0} was True at record time; the live "
                            "callable must be re-supplied at "
                            "bootload".format(flag_name)
                        ),
                    })
        return findings
