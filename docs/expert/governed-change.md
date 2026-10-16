# Preview, stage, and govern structural change

Prerequisites: [research](research.md), [codegen](codegen.md), and
[structural admission](transactions.md). Begin with the existing version's residency,
source, and impact. `research_preview` can combine a candidate analysis with the
selected frame's codegen verdict before any candidate is bound.

The foresight example checks that preview leaves research heads unchanged and the
original pricing object still returns its original result. A malformed candidate
returns parse information that the caller can inspect.

For application checks at registration itself, use the
[bind-hook review pipeline](bind-hooks.md). Its pre callbacks inspect the supplied
reference, activation annotates the new Spell, and post observes the registered result.

## Staging is not promotion

`bind_inactive` places a candidate into the existing SpellIndex while the selected
member remains unchanged, and returns the candidate's spell_id. Expert 17 asserts the
member set, unchanged selection, and unchanged resolved result.

Promotion is `notch_spell(spell_index=..., spell_id=...)` given that spell_id: the
candidate becomes the selected member and the next meld builds it, and a notch back by
the previous spell_id restores the old version, which stayed parked. Expert 17 runs the
whole loop on public calls, as does the README's sketch. Name a parked version by its
spell_id: a lookup by a parked spell_id returns the currently active member.
`notch_spell` refuses a version of another index, or one another Spellbook owns, before
it changes anything. `add_to_spell_index` and `remove_from_spell_index` take `spell_id=`
the same way, to move a parked candidate onto another index or out into one of its own.

## Keep history and code reconciliation distinct

An anchored research lane starts empty. A clean join checks its relation to the
receiver's current tip. A forced join records explicit supersede; it does not
merge source code. Compose and evaluate the candidate first, then record the chosen
outcome through the applicable public operation.

Archive hides a lane from the active view while retaining its history. It is not
runtime object disposal. Keep deliberate version retirement and application
cleanup separate from lane organization.
