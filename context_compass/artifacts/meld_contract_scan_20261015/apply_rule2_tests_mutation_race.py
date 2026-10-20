"""Rule 2 test change: the mid-resolution contract-mutation race forces its pass by a provider-change mark (melder_1).

These tests raced a sever or uncontract against the 5-11 pass the per-meld contract scan forced on every meld of a
contract consumer. With the scan retired, a warm meld of a satisfied consumer compiles nothing, so each test now marks
the consumer as a provider change marks it (the registry call the borrower Book's mutators make) before the forced
meld. contract_recheck_on_notch_2026_10_16. usage: python <this script> <tree root> [--check]
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from apply_lib import apply

ROOT = pathlib.Path(sys.argv[1])
CHECK = "--check" in sys.argv[2:]
REL = "tests/integration/melder/multithreading/test_contract_mutation_during_meld_resolution_integration.py"

STEPS = [
    ("one",
     '''moment later gets. After the contract is restored the consumer melds again.
"""

from threading import Thread
''',
     '''moment later gets. After the contract is restored the consumer melds again.

Since rule 2 (2026-10-16) a warm meld of a consumer whose contract is satisfied runs no resolution pass; only a
consumer a provider change has marked does. Each test therefore marks the consumer the way a provider change marks it
before the meld it forces into the race.
"""

import inspect
from threading import Thread
''', ""),
    ("one",
     '''    def meld_consumer(self) -> Any:
''',
     '''    def mark_consumer_for_recheck(self) -> None:
        """
        Purpose:
            Mark the consumer the way a change of its provider marks it, so its next meld runs a resolution pass.
        Contract:
            - Makes the registry call the borrower Book's contracted-map mutators make
              (`SpellSystemStates.mark_contract_dependents_dirty`) for the consumer's contract key: the consumer
              goes `gated` + `contract_unvalidated` and its Book's validation flag goes up.
            - Changes no contract: the provider stays contracted, so the marked meld's own recheck passes and its
              5-11 pass runs - the pass the race needs.
        Returns:
            None.
        """
        spellbook = self.borrower.spellbook
        contract = inspect.signature(_RaceConsumer).parameters["service"].default
        spellbook._spell_system_states.mark_contract_dependents_dirty(
            spellbook_id=spellbook._id,
            contract_keys={contract.canonical_key},
        )

    def meld_consumer(self) -> Any:
''', ""),
    ("one",
     '''        - Before 0.2.8227 both processors reported the miss as RuntimeError, which the target
          pass could not classify, so the meld raised PhaseExecutionError.
        - After the contract is restored, the next meld resolves the provider again.
''',
     '''        - Before 0.2.8227 both processors reported the miss as RuntimeError, which the target
          pass could not classify, so the meld raised PhaseExecutionError.
        - The forced meld is marked first, as a provider change marks it: since rule 2 a warm meld
          of a satisfied consumer runs no pass.
        - After the contract is restored, the next meld resolves the provider again.
''', ""),
    ("one",
     '''        monkeypatch.setattr(processor_cls, "process", probe.wrap(processor_cls.process))
        with pytest.raises(SpellbookValidationError):
''',
     '''        monkeypatch.setattr(processor_cls, "process", probe.wrap(processor_cls.process))
        world.mark_consumer_for_recheck()
        with pytest.raises(SpellbookValidationError):
''', ""),
]

apply(ROOT, REL, STEPS, CHECK)
