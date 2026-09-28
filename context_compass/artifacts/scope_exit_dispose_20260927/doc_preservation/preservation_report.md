# Content preservation report - scope_exit_dispose_2026_09_27 doc promotion (2026-09-27)

Baselines captured before the first edit (*_before.txt, *_before.md); after-captures span each document
alone (no migration target: nothing was moved out). Every lost line below is a stale claim replaced by
corrected text, a remapped citation, or a remeasured C1 field (end_line/loc/verified_at) in the same
document; none is unaccounted. src_architecture includes the second citation pass
(edit_src_architecture_citations.py).

## src_architecture: 43 lines replaced, 159 lines added
- 1 x `(`bind_frame_configuration` unfrozen branch: the twelve-value copy plus`
- 1 x `- src/melder/aether/aetheric_frame/aetheric_frame.py:645-694`
- 1 x `- src/melder/aether/conduit/conduit.py:5024-5026 (the check and the raise -`
- 1 x `- src/melder/aether/conduit/conduit.py:5075, 5147 (`notch_spell`; starts the transaction)`
- 1 x `- src/melder/aether/conduit/conduit.py:5165, 5220 (`add_to_spell_index`; starts it)`
- 1 x `- src/melder/aether/conduit/conduit.py:5243, 5291 (`remove_from_spell_index`; starts it)`
- 1 x `DIFFERENT object while the existing posture is unfrozen, it copies TWELVE`
- 1 x ``ExceptionGroup` - it is the one teardown here that AGGREGATES failures`
- 1 x `and detach, restore temporary hooks, then publish the ready shell idle. Anonymous leaf return`
- 1 x `checks the name once and performs no Cloud/recorder/Nexus work.`
- 1 x `clears hooks, logger last.`
- 1 x `disposal and the original exception was dropped.`
- 1 x `disposal method, each chained from what that method raised; before, an object's first failure ended its`
- 1 x `end_line: 1136`
- 1 x `end_line: 3813`
- 1 x `end_line: 420`
- 1 x `end_line: 650`
- 1 x `end_line: 6897`
- 1 x `flags, and max_transaction_wait_time_in_seconds - and then calls`
- 1 x `loc: 1136`
- 1 x `loc: 3813`
- 1 x `loc: 420`
- 1 x `loc: 650`
- 1 x `loc: 6897`
- 1 x `note: spellspace scoping.`
- 1 x `rather than stopping at the first, so a single bad object cannot strand the`
- 1 x `rest of the scope. Since 0.2.80 that holds per method too: every declared method`
- 1 x `retain ownership for retry and never publish idle; failed descendants prevent ancestor return.`
- 1 x `rift_enabled, shared_framewide_spellbook_configuration, all six `disable_*``
- 1 x `runs even after one fails, and each failure is chained from what the method raised.`
- 4 x `verified_at: 2026-09-26T20:10:34Z`
- 1 x `verified_at: 2026-09-27T11:46:59Z`
- 1 x `- Cleanup errors are logged; Creations may raise ExceptionGroup. Since 0.2.80 it holds one error per failing`
- 1 x `- SpellSpace can only meld when it is the active spellspace for a Conduit.`
- 1 x `- SpellSpaceScopeError if a non-active SpellSpace is used for meld.`
- 1 x `1. `Conduit.cleanup()` fires hooks, tears down Meld, ConduitWard and Creations,`
- 1 x `1. `conduit.enter_spellspace()` creates and activates SpellSpace.`
- 1 x `2. `SpellSpace.meld(...)` enforces active scope and delegates to Conduit.`
- 1 x `3. `SpellSpace.reset()` clears spellspace-scoped instances and bumps version.`
- 1 x `5. On named return, complete disposal/descendants, retire records and named discovery, clear the name`

## src_components: 74 lines replaced, 212 lines added
- 1 x `(`_sever_link` at :992, `SafeGuard` acquired at :1008, contract lookup at`
- 1 x `(`src/melder/aether/aetheric_frame/aetheric_frame.py:841`; resident member`
- 1 x `- src/melder/aether/aetheric_frame/aetheric_frame.py:209 (DevOpsManager owned)`
- 1 x `- src/melder/aether/aetheric_frame/aetheric_frame.py:750-761`
- 1 x `- src/melder/aether/conduit/conduit.py:5075, 5165, 5243 (public verbs)`
- 1 x `- src/melder/aether/conduit/conduit.py:5124, 5200, 5280 (notch/add/remove`
- 1 x `- src/melder/aether/conduit/conduit_ward/conduit_ward.py:250-283`
- 1 x `- src/melder/aether/conduit/conduit_ward/conduit_ward.py:277-281`
- 1 x `- src/melder/aether/conduit/conduit_ward/conduit_ward.py:283-285`
- 1 x `- src/melder/aether/conduit/conduit_ward/conduit_ward.py:565-567`
- 1 x `- src/melder/aether/conduit/conduit_ward/conduit_ward.py:799, 973`
- 1 x `:1009 - the guard is taken BEFORE the lookup, which is the ordering claim).`
- 1 x `EVIDENCE: src/melder/aether/conduit/conduit.py:5024-5026.`
- 1 x `EVIDENCE: src/melder/aether/conduit/conduit_ward/conduit_ward.py:2508-2562.`
- 1 x `EVIDENCE: src/melder/aether/conduit/conduit_ward/conduit_ward.py:527-580.`
- 1 x `EVIDENCE: src/melder/aether/conduit/conduit_ward/conduit_ward.py:572-579.`
- 1 x `EVIDENCE: src/melder/aether/conduit/conduit_ward/conduit_ward.py:708-721.`
- 1 x `EVIDENCE: src/melder/aether/conduit/conduit_ward/conduit_ward.py:992-1010`
- 1 x `IGNORED rather than rejected, and the warning reports the existing posture`
- 1 x `Other live pairs: `src/melder/aether/conduit/conduit_ward/conduit_ward.py:799` (two peer wards), `:973``
- 1 x ``### Subcomponent: SpellSpace Thread State`.`
- 1 x ``remove_from_index` at `src/melder/aether/conduit/conduit.py:5291`, then calls`
- 1 x ``src/melder/aether/aetheric_frame/aetheric_frame.py:463`) +`
- 1 x ``src/melder/aether/conduit/conduit.py:5147`, then calls `Spellbook._notch_spell(...)`, which delegates`
- 1 x ``src/melder/aether/conduit/conduit.py:5220`, then calls `Spellbook._add_to_spell_index(...)`, which`
- 1 x ``src/melder/aether/conduit/spell_space/spell_space_thread_state.py:245`, and`
- 1 x `a conflicting `AethericFrameConfiguration` for an already-configured frame is`
- 1 x `alongside the attempted one so the discarded intent is recoverable. It is`
- 1 x `catalogued here.`
- 1 x `end_line: 1136`
- 1 x `end_line: 302`
- 1 x `end_line: 3813`
- 1 x `end_line: 650`
- 1 x `end_line: 6897`
- 1 x `end_line: 989`
- 1 x `exception in their Failure Modes; NEITHER owns this file, which is why it is`
- 1 x `has no logger of its own - during early boot the Aether logger may not exist`
- 1 x `i.e. stack corruption, not a user error. Two component entries document that`
- 1 x `it signals STACK CORRUPTION at exit rather than a caller mistake. See`
- 1 x `loc: 1136`
- 1 x `loc: 302`
- 1 x `loc: 3813`
- 1 x `loc: 650`
- 1 x `loc: 6897`
- 1 x `loc: 989`
- 1 x `routed through `self._aether._logger` after a `None` guard, because the frame`
- 1 x `the sole raise site in the tree is `SpellSpaceThreadState`, at`
- 1 x `verified_at: 2026-08-02T16:29:16Z`
- 4 x `verified_at: 2026-09-26T20:10:34Z`
- 1 x `verified_at: 2026-09-27T11:46:59Z`
- 1 x `yet.`
- 1 x `- Cleanup fires hooks, tears down Meld, ConduitWard, Creations, then logger.`
- 1 x `- Cleanup is best-effort; errors are suppressed to complete teardown.`
- 1 x `- EXACTLY ONE log call in the whole module, and it is a `warning`, not an error:`
- 1 x `- Enforce spellspace activation for unique_per_spell_space.`
- 1 x `- IT IS THE SOLE RAISER OF `SpellSpaceScopeError` in the entire tree, at`
- 1 x `- No explicit lock; owner Conduit lock used upstream.`
- 1 x `- SpellSpace cleanup resets scope and unregisters from owner.`
- 1 x `- SpellSpace id and version counter.`
- 1 x `- `SafeLogger` with 79 `error` sites and, unusually for this codebase, 11 `info``
- 1 x `- `SpellSpace.meld()` checks active scope and delegates to Conduit.`
- 1 x `- `SpellSpaceScopeError` if scope is misused. NOT RAISED BY THIS COMPONENT -`
- 1 x `- `create_lesser_conduit(...)`.`
- 1 x `1. `Conduit.create_lesser_conduit(...)` fires pre-create hook.`
- 1 x `1. `conduit.enter_spellspace()` creates and activates a SpellSpace.`
- 1 x `2. `SpellSpace.meld(...)` verifies it is the active scope.`
- 1 x `3. Delegates to `Conduit.meld(...)` for resolution.`
- 1 x `4. `SpellSpace.reset()` clears spellspace-scoped instances and increments version.`
- 1 x `Failed descendants prevent ancestor return. Hook restoration and idle publication remain last.`
- 1 x `Named soft return runs Space/creation disposal and descendant cleanup first, then structural`
- 1 x `_prepare_for_pool disposes Spaces and creations first, clears local lifecycle overlays, restores`

## tests_components: 5 lines replaced, 37 lines added
- 1 x `(0.2.80)`
- 1 x `end_line: 120`
- 1 x `loc: 120`
- 1 x `verified_at: 2026-09-27T13:27:50Z`
- 1 x `above - 183 paths - and nothing else. Change a component's key files and this set`

