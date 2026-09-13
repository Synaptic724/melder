# Dynamic bind/conjure order benchmark

Compare five individual binds, one dynamic conjure, and the first meld of each object.
Both cases use the same public Spellbook.bind API and returned spell ids for Conduit.meld.
Fresh frame/book construction and deterministic cleanup are outside the timed workflow.
Disk system caching, Crystallizer recording and Nexus publication are disabled. GC stays enabled.
Use the repository's default five compiler workers and CPython 3.14 free-threaded with GIL off.
Warm-up pairs precede measured pairs; case order alternates AB/BA to balance time/order effects.
Any repeated cached meld measurements are separate from the requested first-meld/total comparison.
Save every sample and metadata per process; report medians and distribution bounds, not fastest-only numbers.
