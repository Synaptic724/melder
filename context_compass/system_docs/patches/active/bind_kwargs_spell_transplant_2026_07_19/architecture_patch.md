# Architecture Patch: bind-kwargs pass through to the spell object

Lane: bind_kwargs_spell_transplant_2026_07_19.
Ticket: STORY-2026-07-19-bind-kwargs-transplant (to be opened at implementation).

## Objective (owner ruling, 2026-07-19, refined in-session)
bind(**kwargs) leftovers (after the reserved hook transfers pop) are construction
arguments FOR THE USER'S SPELL OBJECT - not binding metadata, not Spell-record
semantics. They are carried opaquely and passed into the spell object at creation:
bind(spell=SmtpMailer, host="x", port=1) means SmtpMailer(host="x", port=1) when the
spell creates. "Its literally only for the spell object, not the binding object."

## Semantics
1. Spellbook.bind pops pre_hooks/activation_hooks/post_hooks (unchanged).
2. The remainder is stored on the Spell AS AN OPAQUE CONSTRUCTION PAYLOAD - the Spell
   carries it; it means nothing to the binding itself.
3. At creation, the payload is passed into the spell object:
   - class spells: UserClass(**payload)
   - callable spells: user_callable(**payload)
   - instance spells: nothing constructs -> a non-empty payload FAILS (the spell
     object cannot accept construction args).
4. Rejection comes FROM THE SPELL OBJECT's own signature: an unknown key fails as the
   object's TypeError. Eager bind-time pre-check against the object's signature is an
   implementation option for fail-fast timing, but the authority is the user object's
   signature, never melder-side vocabulary.
5. Precedence at creation: meld(spell_override=...) > bind payload > signature
   defaults. Call site wins per-key.
6. Persistence: the payload rides the crystal record as opaque construction args
   (JSON-serializable verbatim; non-serializable -> honest marker), so restored
   worlds construct identically.
7. Explicitly OUT: the payload does NOT join binding identity, fingerprints, or the
   DuplicateSpellNameStrategy story - that ruling (decision A) stands alone.

## Blast radius
Bind._bind_logic / _add_hooks_to_spell (pop + store), Spell (carry payload + cleanup),
creation compile (merge payload under meld spell_override - the overrides lane
exists), SpellCrystal record round-trip, UX harness probes (silent-swallow probe
flips: unknown key on a class spell fails from the object's signature; class-kwarg
delivery, callable-call kwargs, instance rejection, precedence rows).

## Rollback
Revert to hook-only kwargs reading; probes flip back to the silent-swallow pins.
