# Architecture Patch: lazy default frame + Aether LoadGate

- Patch ID: aether_lazy_frames_and_load_gate_2026_07_11
- Tickets: TASK-2026-07-11-lazy-default-aetheric-frame (lazy frames),
  STORY-2026-07-11-load-scope-maturity (LoadGate; transaction-awareness
  ruling folded from the owner's 2026-07-11 direction)
- Status: active

## Objective
Two sibling substrate changes at the Aether/mediator seam:
A) LAZY FRAMES (owner: the eager default frame "wasn't intended"): import
   creates ZERO AethericFrames; the first Spellbook births the frame it
   names; collapsed configuration falls back to "default".
B) LOADGATE (owner: "if there is a load happening we give all rights to the
   thread that's executing that load"): one Aether-hosted exclusive gate
   that every frame-local TransactionMediator consults at ROOT starts -
   the loading thread passes free, everyone else waits (bounded).

## Non-goals
- No transaction family, no per-family claim rows (superseded design).
- No change to per-verb self-admission inside loads (they keep running so
  registry mirrors and commit deltas stay correct).
- No behavior change when no load is in flight and no gate is threaded
  (all new ctor params default to None).

## Invariants
- Claims never cross frame planes (unchanged); the gate is ABOVE planes.
- Aether constructs the gate BEFORE any frame can exist, so the gate
  covers frames born mid-load unconditionally (bootstrap-proof).
- Cleaned-singleton refusal survives lazy frames via _ensure_frame's
  check_cleaned.

## Interface Deltas
- NEW utilities/synchronization/load_gate.py: LoadGate (Cleanable):
  acquire(label) [exclusive, reentrant-per-thread refusal on double
  acquire], release(), wait_for_passage(timeout) [passes when open OR
  caller is the holder thread; RuntimeError on timeout naming the holder
  label], describe().
- Aether: eager default-frame construction DELETED (:121-123);
  _ensure_default_frame lazily creates via _ensure_frame("default")
  [SEMANTIC CHANGE, owner-flagged: individually-cleaned default frame now
  RECREATES on next use instead of raising - matches named-frame
  semantics]; NEW owned _load_gate (constructed before anything frame-
  bearing) + acquire_load_authority(label)/release_load_authority() verbs
  with drain (poll live frames' mediator active-session counts to zero,
  bounded, sliced).
- Ctor threading (all additive, default None): AethericFrame passes
  aether's gate into DevOpsManager(load_gate=) ->
  ChangeControlManager(load_gate=) -> TransactionMediator(load_gate=).
- TransactionMediator: ROOT starts (begin_transaction new-root path,
  begin_frame new-root path) call load_gate.wait_for_passage(bounded by
  _max_transaction_wait_time_in_seconds) when a gate is threaded. Nested
  joins never gate.
- CrystalLoaderSystem(persistence_system, aether=None): load verbs wrap
  plan+execute in acquire_load_authority/release (try/finally); None
  aether = ungated (unit suites unchanged).
- Crystallizer passes its _aether into the loader child.

## Migration Order
1. LoadGate class -> 2. Aether hosting + lazy-frame edits -> 3. mediator
chain threading + root-start check -> 4. loader/crystallizer integration
-> 5. tests (new unit: gate + lazy frames; sweep: boot-count assumptions).

## Rollback
All deltas additive or localized; reverting restores eager frame + ungated
mediators byte-identically.

## Ticket Coverage
- tickets/tasks/2026-07-11_lazy_default_aetheric_frame_task.md (findings)
- tickets/stories/2026-07-11_load_scope_maturity_story.md (12:30Z + 12:45Z
  notes carry the mediator mechanics + bootstrap evidence)
