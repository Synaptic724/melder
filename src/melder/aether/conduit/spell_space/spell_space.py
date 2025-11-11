class SpellSpace:
    """
    SpellSpace is a fast, lightweight execution boundary created by a Conduit for casting short-lived spells.
    threadsafe and isolated from the main conduit state, allowing for rapid instantiation and disposal of spell objects.

    🧙 Purpose:
    - Create a scope for rapidly instantiated and disposable spell objects.
    - Prevent long-lived pollution of the conduit’s state.
    - Enable safe, parallel execution in multithreaded environments.

    🧠 Key Features:
    - Each SpellSpace is isolated from others (thread-safe by design).
    - Conduits can create multiple spellspaces — one per thread or task.
    - Objects created inside a SpellSpace are automatically discarded on reset.
    - Normal conduit-linked objects are not affected.

    🚦 Lifecycle:
    1. `create()`: Start a new spellspace.
    2. `cast(spell)`: Meld spells using this isolated scope.
    3. `reset()`: Clear all spellspace-bound objects.
    4. `close()`: Final disposal; spellspace becomes cleaned.

    🔁 Ownership:
    - All spellspace objects belong *only* to the SpellSpace, not to the Conduit.
    - When the SpellSpace is reset or closed, all internal objects are cleaned up.
    - This avoids contamination of the conduit or Aether.

    ⚠️ Enforcement:
    - Meld operations for SpellSpace spells are only valid *within* the context of the active SpellSpace.
    - Attempting to meld a spellspace-only spell outside of a valid context should raise an error.

    🧵 Multithreading Support:
    - Each thread can independently create and manage its own SpellSpace.
    - Conduits can maintain a ConcurrentDict of active spellspaces if tracking is desired.

    🛠️ Bootstrap Example:
        spellspace = conduit.create_spellspace()
        spellspace.cast(MySpell)
        spellspace.cast(AnotherSpell)
        spellspace.reset()  # Reset the spellspace without closing it
        spellspace.close()  # Fully dispose and cleanup the spellspace

    This system enables fast, scoped object casting with guaranteed cleanup — ideal for high-frequency or time-bound tasks.

        🧬 Versioning & Isolation (Advanced Concept):
    - SpellSpaces can optionally maintain a `version` field that increments with each `reset()` call.
    - This allows spells to distinguish between stale vs fresh contexts.
    - Especially useful for implementing `unique_per_spell_space_refresh` strategy without recreating the SpellSpace.

    🧠 ContextVar Integration:
    - Internally, a `ContextVar[SpellSpace]` is used to bind the current active spellspace to the executing thread or coroutine.
    - This allows `conduit.meld()` to introspect whether it’s inside an active spellspace and route instantiation logic accordingly.

    💡 Best Practice:
    - Always enter a spellspace via a context manager:
        with conduit.enter_spellspace(): ...
      This ensures proper reset and disposal.
    - Directly calling `create()` is fine for manual lifecycle control, but remember to reset and close!

    🧹 Memory Safety Tips:
    - Use `.reset()` or `.close()` to fully release internal object references.
    - Avoid storing large models or long-lived tasks inside the spellspace unless disposal is guaranteed.
    - Consider adding a `.cleanup()` method to spellspace-bound objects if they need explicit teardown.

    🧪 Debugging & Tracing:
    - Add debug flags or attach a monitor to log spellspace creation/reset/close events.
    - Tracking active SpellSpace `id`, `version`, and object count can help detect leaks or misuse.
    - `__del__` or `__repr__` overrides can be helpful in development mode.

    🌀 Reminder:
    - SpellSpaces are **ephemeral scoped containers**, not global registries.
    - Their purpose is to isolate creation logic in high-performance or parallel contexts.
    - Use them like you would use a short-lived container or service scope in traditional DI frameworks.

    ✅ Summary:
    - SpellSpaces are thread/task-local DI boundaries.
    - Great for per-request or short-lived pipelines.
    - Versioning helps manage refresh cycles.
    - `ContextVar` ensures automatic thread/task tracking.
    - Clean them up and they’ll serve you well.

    """
