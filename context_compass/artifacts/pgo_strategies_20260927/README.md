# PGO strategy exploration artifacts

- `vm_composition_run_gil0_20260927.md`: full output of
  `tests/experimentation/pgo_codegen_composition_experiment.py` on the VM (CPython 3.14.7t, GIL disabled,
  2 cores, melder 0.2.82, iters=20000 repeats=5 warmup=2000 sample=50, threads 1 and 2). Directional numbers;
  the owner's box decides.
- `warm_meld_call_trace_20260927.md`: the Python and C calls one warm meld makes (solo, wide8_singleton).
- `melder_composition_scan_20260927.md`: output of `tests/experimentation/pgo_composition_scanner.py src/melder`
  (static AST scan of Melder's own 612 classes: constructor width, chain depth, tree size, inheritance depth,
  and the experiment's ceiling per width bucket).
- `vm_melder_shaped_run_mro0_20260927.md` / `..._mro2_...`: the experiment on shapes matching Melder's own
  width distribution (solo, w1, w2, w3, w4, chain3, mixed3s4t), weighted by the scanner's shares, at
  inheritance depth 0 and at depth 2 (a base chain with `super().__init__()`, Melder's usual). VM, directional.
- `door_and_site_attribution_20260927.md`: the door split into its frames and one singleton site in isolation;
  corrects the per-site estimate to 8-16 ns.
- `vm_meld_entry_dispatch_run_gil0_20260927.md`: output of `tests/experimentation/meld_entry_dispatch_experiment.py`
  - today's `conduit.meld` by name, class and id against a prototype one-lookup entry over the real runtime
  objects (real fast-door entries, real builders, real epoch and context guards). VM, directional.
- `vm_meld_entry_dispatch_after_change_gil0_20260927.md`: the same experiment after the name/class registry
  landed (task meld_entry_cache_by_name_and_class): `today_by_name` and `today_by_class` now ride
  `Conduit.meld`'s warm lane; before/after per shape is in the task's MEASURE note. VM, directional.
- `vm_opt_in_specializer_by_name_gil0_20260927.md`: the EXISTING opt-in singleton specializer
  (`generalized_singleton_specialization_enabled`, default False) measured by name, off vs on, after the name/class
  lane landed: -14% on wide8_singleton, -2..-3% on w1/w2/w4, +20% on chain8_singleton (a regression the naive
  always-on selection cannot see). VM, directional.
- `vm_probe_overhead_prototype_gil0_20260927.md`: output of `tests/experimentation/probe_creation_context_prototype.py`
  - the real emitted normal plan instrumented as a count-only probe (+18..+49 ns per call) and a timed probe
  (+181..+771 ns per call, `perf_counter_ns` = 33 ns), against the plain plan and today's meld by name. VM, directional.
- `vm_commandops_melc_ledger_gil0_20260927.md`: output of `tests/experimentation/melc_cache_ledger.py` over the
  commandops application's real `__melder_cache__` (melder 0.2.77, generation 15, 9 bundles): per cached root,
  what its emitted normal plan does per creation (shared reads, inline constructors, disposal registrations,
  width, depth) priced with the live numbers below. 51 generalized roots: 47 singletons (bodies once per scope),
  4 `many` roots, all four registering for disposal every creation. Static proof, no runtime probe.
- `vm_commandops_shapes_gil0_20260927.md`: output of `tests/experimentation/commandops_shape_probe.py` - the two
  commandops `many` shapes rebuilt live (Worker(manager); ContextRoot over 4 existing objects + 1 unique), with and
  without a disposal method, plain and with the opt-in specializer: the disposal registration is 400-690 ns of a
  650-1220 ns meld; the specializer is mixed-to-negative on these shapes. Two runs; VM, directional.
- `vm_many_registration_split_gil0_20260927.md`: output of
  `tests/experimentation/many_registration_split_experiment.py` - the emitted `add_many_creations(...)` call priced
  against a real `Creations` store (305-384 ns with disposal, 151-185 without), the RLock alone (57-67), and two
  trimmed stand-ins: per-key methods with one append under the lock (103-120) and lock-free append after a
  double-checked first use (62-63). VM, directional.
