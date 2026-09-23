# Conduit bind-hook facade patch

## Owner requirement
Every new public Spellbook API in this feature must have its matching Conduit facade. This adds
add_bind_hooks(pre=None, activation=None, post=None) and clear_bind_hooks(). Private Book emission
helpers remain internal.

## Before and after
Conduit already forwards bind/bind_inactive but cannot configure their new lifecycle. The new methods
check liveness and normal ownership, then delegate unchanged to the existing owning Spellbook.
There is no duplicate callback registry, direct Bind manipulation or additional transaction envelope.

## Ownership and admission
Normal conduits own their Book; lessers borrow one and cannot configure its bind policy. A cleaned or
lesser conduit refuses before delegation. Hook setup itself follows Book's live-update contract even
on an automatic root; the existing bind verb still independently refuses when posture disables bind.
User callbacks and current-operation snapshot behavior remain entirely Book/Bind responsibilities.
Conduit facade calls acquire no additional object lock around Book/Bind's own coordination.

## Recording and existing hooks
Delegation uses the Book producer, so clear/re-add updates the existing complete book twin. No change
to register_conduit_hooks, Meld runtime hooks or per-Spell creation hooks is included here.

## Validation mapping
Real-root facade registration -> active/inactive/direct-Book binding; Book-configured hooks cleared
through Conduit; re-registration; lesser/cleaned refusal without changing owner callbacks; automatic
setup with actual bind still refused; invalid callback forwarding and Crystallizer late-update parity.
Build assets, graph and indexes remain held for owner code approval.
