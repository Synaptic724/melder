# Research: Fast-path eligibility gates (validity + change control + hooks)

Date: 2026-01-25

## Scope
Capture existing gating checks in Meld and MeldRuntime that must be honored
before executing a compiled plan.

## Evidence
- src/melder/aether/conduit/meld/meld.py:Meld._ensure_lineage_resolvable
- src/melder/aether/conduit/meld/meld.py:Meld.meld
- src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py:MeldRuntime.execute
- src/melder/aether/dev_ops/change_control_manager/change_control_manager.py

## Findings
- Meld._ensure_lineage_resolvable enforces SpellSystemState gating and runs
  structural phases (1-4) and resolution phases (5-7) when validity is
  UNKNOWN or GATED (docstring and flow).
- MeldRuntime.execute performs system-level gating when
  spell._spellbook._spellbook_validation_required is True, including
  SpellValidity invalid/gated/disabled checks and change-control dirty root
  checks, then enforces spell.is_broken and spell.validated.
- Meld.meld selects hook vs non-hook execution paths based on
  self._meld_hooks or target_spell._hooks_enabled.

## Unknowns
- UNKNOWN: Fast-path eligibility rules for hook-enabled spells (plan variant vs
  forced fallback).
  - Why it matters: hook execution ordering is part of public behavior.
  - Where to investigate: src/melder/aether/conduit/meld/meld.py:
    _comprehensive_meld_with_hooks and hook execution helpers.
  - Status: uninvestigated.

- UNKNOWN: Whether an optimistic cache hit can be made lock-free without
  violating Creations thread-safety contracts.
  - Why it matters: lock-free cache checks are a primary performance target.
  - Where to investigate: src/melder/aether/conduit/creations/creations.py and
    src/melder/aether/conduit/creations/lesser_creations.py.
  - Status: uninvestigated.
