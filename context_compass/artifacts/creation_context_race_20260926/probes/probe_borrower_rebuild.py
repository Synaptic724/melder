"""Sequential (no threads) trace: does a borrower's first meld rebuild the owner's shared spell plan and context?

Owner + N borrowers, one Existence.many spell shared by contract, exactly as the concurrency test sets it up.
Wraps CompilerPhase5.run_local / run_frame_wide and CreationContextFactory.get_or_build_for_spell to log calls, and
records the shared plan's executor signatures and the context object identity after every meld.
Run from the repository root with the tests package importable (PYTHONPATH=src:.).
"""
import hashlib
import json
import sys


def main() -> None:
    """Run owner meld, then each borrower's first meld, then owner again; print one JSON trace."""
    from melder.aether.aether import Aether
    from melder.aether.spellbook.existence.existence import Existence
    from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
    from melder.aether.spellbook.spellbook import Spellbook
    from melder.aether.spellbook.spell_compiler.phases.compiler_phase_5 import CompilerPhase5
    from melder.aether.conduit.meld.creation_context.creation_context_factory import CreationContextFactory
    from tests._frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration
    from tests.mocks.spellbook.core_classes import BasicService

    events = []
    original_run_local = CompilerPhase5.run_local
    original_run = CompilerPhase5.run_frame_wide
    original_get_or_build = CreationContextFactory.get_or_build_for_spell

    def run_local(self, spell, artifact, spellbook, spell_system_states, conduit_id, cancel_event=None):
        events.append({"event": "phase5.run_local", "conduit": conduit_names.get(conduit_id, conduit_id)})
        return original_run_local(self, spell, artifact, spellbook, spell_system_states, conduit_id, cancel_event)

    def run(self, *args, **kwargs):
        events.append({"event": "phase5.run_frame_wide"})
        return original_run(self, *args, **kwargs)

    def get_or_build(self, spell):
        state_before = spell._creation_context_switch.state
        context = original_get_or_build(self, spell)
        events.append({"event": "factory.get_or_build", "switch_before": state_before})
        return context

    CompilerPhase5.run_local = run_local
    CompilerPhase5.run_frame_wide = run
    CreationContextFactory.get_or_build_for_spell = get_or_build

    def make_book() -> Spellbook:
        configuration = Aether()._get_configuration("default")
        if configuration is None:
            configuration = SpellbookConfiguration()
            apply_dynamic_defaults_for_spellbook_configuration(configuration)
        return Spellbook(configuration=configuration)

    def snapshot(label: str) -> None:
        creation = spell._compiler_artifact._spell_codegen_creation
        metadata = creation.metadata if creation is not None else {}
        events.append({
            "event": "after " + label,
            "context_id": id(spell._creation_context) if spell._creation_context is not None else None,
            "codegen_id": id(creation) if creation is not None else None,
            "no_overrides_signature_sha": hashlib.sha256(
                repr(metadata.get("_no_overrides_executor_signature")).encode()).hexdigest()[:16],
            "override_rows_signature_sha": hashlib.sha256(
                repr(metadata.get("override_steps_rows_signature")).encode()).hexdigest()[:16],
        })

    conduit_names = {}
    owner_book = make_book()
    spell_id = owner_book.bind(spell=BasicService, existence=Existence.many, permissions="create")
    owner = owner_book.conjure(dynamic=True, name="owner")
    conduit_names[owner.id] = "owner"
    spell = owner_book._spell_id_pool[spell_id]
    borrowers = []
    for index in range(2):
        book = make_book()
        borrower = book.conjure(dynamic=True, name=f"borrower-{index + 1}")
        conduit_names[borrower.id] = f"borrower-{index + 1}"
        owner.link(borrower)
        with borrower.transaction("link", conduits=[borrower, owner]):
            borrower.add_spell_to_contract(spell_id=spell_id, conduit=owner, permissions="create")
        borrowers.append(borrower)
    events.append({"event": "setup done"})
    owner.meld(spell_id=spell_id)
    snapshot("owner meld 1")
    for borrower in borrowers:
        borrower.meld(spell_id=spell_id)
        snapshot(conduit_names[borrower.id] + " meld 1")
    owner.meld(spell_id=spell_id)
    snapshot("owner meld 2")
    for borrower in borrowers:
        borrower.meld(spell_id=spell_id)
        snapshot(conduit_names[borrower.id] + " meld 2")
    json.dump(events, sys.stdout, indent=1)


if __name__ == "__main__":
    main()
