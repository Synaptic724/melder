"""Rule 2 / D3 source change in conduit.py: a notch back makes a peer's parked copy of the incoming version active again.

`Conduit.notch_spell` calls the new `_activate_borrowed_spell` after the deactivate fan-out and before the ward's
index emission, so a version grant parked by a notch away comes back on the notch back, and its consumers are marked
(the peer Book's `_reactivate_contracted_spell`). contract_recheck_on_notch_2026_10_16,
component_patch_notch_reactivation. Applies after melder_0's notch-target landing (conduit.py custody).
usage: python <this script> <tree root> [--check]
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from apply_lib import apply

ROOT = pathlib.Path(sys.argv[1])
CHECK = "--check" in sys.argv[2:]
REL = "src/melder/aether/conduit/conduit.py"

STEPS = [
    ("one",
     '''            - After the window, every linked peer parks its copy of the outgoing version and
              index-link borrowers move to the new one, which they build at their next meld.
''',
     '''            - After the window, every linked peer parks its copy of the outgoing version, a
              peer holding a parked copy of the incoming version (a grant of that version) has
              it made active again, and index-link borrowers move to the new one. The consumers
              of every copy that changed are marked and revalidate at their next meld; objects
              already built keep what they were built with (rule 2, 2026-10-16).
''', ""),
    ("one",
     '''        # conduit -- the only thing that knows about links -- walks its peers so
        # each borrower's spellbook parks its now-stale borrowed copy.
''',
     '''        # conduit -- the only thing that knows about links -- walks its peers so
        # each borrower's spellbook parks its now-stale borrowed copy and makes a
        # parked copy of the incoming version active again.
''', ""),
    ("one",
     '''        if outgoing_id is not None and outgoing_id != spell.spell_id:
            self._deactivate_borrowed_spell(outgoing_id)
            # Index-link receivers follow the lineage: move their subscription head
''',
     '''        if outgoing_id is not None and outgoing_id != spell.spell_id:
            self._deactivate_borrowed_spell(outgoing_id)
            # Outgoing first, so no peer holds two active copies under one key. A version
            # grant parked by an earlier notch away comes back here (D3, 2026-10-16); the
            # peer Book's reactivation marks the copy's consumers for revalidation.
            self._activate_borrowed_spell(spell.spell_id)
            # Index-link receivers follow the lineage: move their subscription head
''', ""),
    ("one",
     '''            peer_spellbook._inactivate_contract_spell(owner_id, spell_id)

    def sever_link(self, target_conduit: "Conduit") -> bool:
''',
     '''            peer_spellbook._inactivate_contract_spell(owner_id, spell_id)

    def _activate_borrowed_spell(self, spell_id: str) -> None:
        """
        Internal

        Owner-side borrower fan-out, the mirror of `_deactivate_borrowed_spell`: walk
        this conduit's active links and make every peer's PARKED contracted copy of
        `spell_id` active again. When this conduit notches an index back to a version a
        peer was granted (`add_spell_to_contract`, a version grant), the copy the notch
        away parked becomes that peer's active copy once more (D3, 2026-10-16); a grant
        of a version that was parked when it was made becomes active the same way.

        Contract:
            - `notch_spell` calls it after the notch transaction and after the
              deactivate fan-out, so a peer never holds two active copies under one key.
            - The per-peer call (`Spellbook._activate_contract_spell`) is idempotent: a
              no-op for a peer holding no parked copy of `spell_id`, so a peer that never
              borrowed the version, or already holds it active, is untouched.
            - The reactivation is the peer Book's `_reactivate_contracted_spell`, which
              marks the consumers of the copy's key `gated` + `contract_unvalidated`
              (rule 2): their next meld revalidates and rebuilds against the copy.
              Objects already built are untouched.
            - An index-link receiver holding a parked copy of `spell_id` gets it back
              here; `ConduitWard._emit_index_notch` then finds it active, the end state
              that emission reached on its own before.

        Threading:
            Takes no lock of its own. The ward's link listing (`_get_links`) holds the
            ward lock for the read only; each peer Book takes its own lock inside the call
            and releases it before the mark, as in the deactivate fan-out.

        Args:
            spell_id (str): Version id of the spell whose parked borrowed copies to make
                active again (the notch's incoming version).

        Returns:
            None.

        Raises:
            RuntimeError: If this conduit, or a linked peer's Spellbook, has been cleaned.
        """
        self.check_cleaned()
        owner_id = self._id
        for peer in self._conduit_ward._get_links():
            peer._spellbook._activate_contract_spell(owner_id, spell_id)

    def sever_link(self, target_conduit: "Conduit") -> bool:
''', ""),
]

apply(ROOT, REL, STEPS, CHECK)
