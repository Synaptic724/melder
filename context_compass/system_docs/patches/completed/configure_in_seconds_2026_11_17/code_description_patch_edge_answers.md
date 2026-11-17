# code_description_patch_edge_answers

## Metadata
- Patch ID: configure_in_seconds_2026_11_17
- Component: `ModuleAnswerCache` edge answers, `CrystalAnalyzer._resolve_pass_edge`, `DependencyViewStrategy`
- Owner: Mark (accountable); melder_0 (synaptic_python_developer)
- Ticket: https://github.com/Synaptic724/melder/issues/331
- Created: 2026-11-17T12:05:00Z
- Updated: 2026-11-17T12:32:22Z

## Control Flow Commitments
- `_resolve_pass_edge(name, obj)`: the per-pass map first (unchanged). On a miss, when `_answer_policy_key` is set
  and `obj` is not a `SyntheticModule`, read `obj.__file__` text and ask `lookup_edge_answer`; on a hit build
  `(name, obj, path, self._custody_by_kind[kind], leaf)`, keep it in the pass map, return it. Otherwise compute as
  today and, under the same conditions, `store_edge_answer(policy_key, name, obj, file_text, path, kind, leaf)`.
- `lookup_edge_answer` under the cache lock: the entry for (policy key, name); its module reference must
  dereference to `obj` (`is`), or both be absent; its `__file__` text must equal; with no object, `sys.path` must
  equal the kept tuple. A failed guard returns None (the caller recomputes and replaces). A hit moves the entry to
  the LRU's recent end.
- `finalize`: count each walked module's walked dependencies, heapify the ready names, pop the smallest, decrement
  its dependents (in any order), push a dependent at zero; append the unresolved names sorted and record the cycle
  error exactly as before.

## Edge and Error Semantics
- A relative `__file__` is never kept (it resolves against the working directory), as for the path entry.
- Strategy lookup by kind uses the analyzer's own strategies; an answer is stored only for default chains.

## Invariants and Idempotency
- Last store wins under the lock; values only (path objects, strings, tuples) plus weak references.
- The heap pops names in ascending order among the ready set, exactly the order the sorted list produced.

## Explicit Non-Goals
- No reuse of facts or worlds beyond 0.2.8305's rules; no change to what a walk records or to a walk's visit order.
