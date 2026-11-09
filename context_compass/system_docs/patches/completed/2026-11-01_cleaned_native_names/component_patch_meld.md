# Meld Resolution Runtime contract
<!-- BEGIN ENTRY: "Meld terminal validity reference" -->
## Purpose and boundary
Only SpellValidity.cleaned references inside native Meld.
## Before and after
Replace typed terminal member references with SpellValidity.CLEANED.
## Interface and errors
Every existing meld refusal, validation result and error text remains; no new fallback.
## State and lifecycle
No new cleanup behavior, resolution gate, lock, lease or retained object.
## Failure delta
No behavioral delta beyond the member's canonical Python name.
## Dependencies and order
Read the complete Meld implementation before editing, then land with SpellValidity.
## Validation and unknowns
Run complete affected Meld tests and terminal gates; full implementation read is pending.
<!-- END ENTRY: "Meld terminal validity reference" -->
