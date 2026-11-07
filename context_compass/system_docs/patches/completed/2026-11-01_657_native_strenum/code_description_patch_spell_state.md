# Spell state flag dispatch

<!-- BEGIN ENTRY: "Preserve flag owner across equal string families" -->
## Control flow
Inside the existing state lock, has_flag returns False for a non-SpellState member.
Both flag mutation paths add or discard only actual SpellState members, keeping the
existing add-before-remove order and None-ignore behavior. A non-family addition was
previously retained and is now ignored; disclose it. No lock or callback moves.

## Validation
Use same-named SpellStateChangeReason and raw string values to prove they cannot
observe or remove a valid flag; valid SpellState members must still add/remove it.
Test actual set_validity and update_flags transitions and legacy numeric pickles.
<!-- END ENTRY: "Preserve flag owner across equal string families" -->
