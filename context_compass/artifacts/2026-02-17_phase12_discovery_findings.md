# Phase 12 & CreationContext Codegen Optimization Discovery Findings

## 1. Benchmark Baseline Analysis

**Run Date:** 2026-02-17
**Script:** `benchmarks/testing_other_di/run_codegen_benchmark_deltas.py`

### Key Metrics (Sample: 50 Iterations)

| Metric | Efficient/Fast Path | Native/Hot Path | Slow/Cold Path | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Warm Execute (Root)** | ~500 ns | - | - | Very fast. Direct `no_overrides` path seems optimal. |
| **Warm Execute (Mixed)** | - | ~20,000 ns (20 \u00b5s) | - | Sign of overhead when mixing override/no-override or different shapes. |
| **Warm Override (Targeted)** | ~2,500 ns (2.5 \u00b5s) | - | - | 5x slower than Root execution. Good target for optimization. |
| **Warm Override (Root Args)** | ~1,900 ns (1.9 \u00b5s) | - | - | Similar to Targeted. |
| **Cold Compile** | - | - | ~6,500,000 ns (6.5 ms) | Compilation cost is significant. Reducing generated code size/complexity helps here. |

*Note: `SpellSpace` metrics (~20\u00b5s) are excluded from this analysis per user directive.*

## 2. Code Analysis: Phase 12 Executors

### `phase12_no_overrides_executor.py`
- **Current State:**
    - Generates a linear sequence of steps.
    - Inlines existence checks (good).
    - **Inefficiency:** Calls `_construct_spell_instance` for *every* step to resolve dependencies and invoke the spell.
        - This helper function builds `kwargs` dict at runtime by iterating over `dependency_resolution_order`.
        - It performs runtime checks for `is_existing_creation`, `is_class_spell`, etc.
        - It wraps the call in a `try...except` block every time.
- **Optimization Opportunities:**
    - **Deep Inlining:** Port the logic from `phase12_overrides_executor.py` (specifically `_append_no_overrides_kwargs_inline_source` and `_append_overrides_invoke_source`) to this file.
    - **Compile-Time Resolution:**
        - If `dependency_resolution_order` is known, emit `arg=instance_results[...]` directly in the call signature, avoiding intermediate `kwargs` dict.
        - If `spell` is a constant/value (not callable), emit direct assignment.
        - Remove `try...except` blocks for "trusted" internal spells if appropriate (or inline them).

### `phase12_overrides_executor.py`
- **Current State:**
    - Already contains advanced pathing for inlining `kwargs` construction and invocation (`_append_overrides_invoke_source`).
    - **Bottleneck:** The "Mixed Execute" benchmark suggests overhead when switching between these paths or managing the override map state.
- **Optimization Opportunities:**
    - **Review Inlining Usage:** Ensure that *all* paths in the overrides executor actually use the inlined logic and don't fall back to `_construct_spell_instance_with_overrides` unnecessarily.
    - **Shape Specialization:** Further specialize generated code for specific override counts (1 or 2 targets) to avoid general dict iteration loop overhead in `CreationContext`.

## 3. Code Analysis: CreationContext Codegen
- **Current State:**
    - Uses template-based generation (`_build_creation_context_template_source`).
    - Wraps the Phase 12 executor with checks for `unique_per_conduit`, `shared`, etc.
- **Observations:**
    - The wrapper adds a function call layer.
    - `unique_per_conduit` and `shared` paths use direct dictionary lookups (efficient).
- **Optimization Opportunities:**
    - **Leaf Inlining:** If the `no_overrides_executor` for a specific spell is "simple" (e.g., just one step returning an instance), we could technically inline that logic into the CreationContext wrapper itself, saving one function call frame. However, this adds significant complexity for a smaller gain compared to fixing the Phase 12 executor iterator loop.

## 4. Proposed Strategy

### Primary Target: `phase12_no_overrides_executor.py`
This is the "Execution Engine" for most standard meld calls. Optimizing this yields benefits across the board.
1.  **Refactor Generation Logic:** Import or duplicate the inlining logic from `phase12_overrides_executor.py`.
3.  **Implement `_append_construct_spread_source`:**
    - **Status:** **DONE** (Implemented as `_append_construct_inline_source`).
    - **Details:** Replaced `_construct_spell_instance` with inline kwargs construction and invocation.
    - **Result:** Benchmark passed. Hot path (`warm_execute`) remains fast (~400-500ns). `_construct_spell_instance` is now dead code.

### Secondary Target: `creation_context_codegen.py`
1.  **Review Overheads:** Ensure that the wrapper templates are not re-checking things that the inner executor might also check (though separation of concerns suggests the wrapper handles "scope" and the inner executor handles "construction").

## 5. Next Steps
- **Plan:** Create implementation tasks for "Phase 12 No-Overrides Inlining".
- **Documentation:** This artifact serves as the discovery record.
