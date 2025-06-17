#    Copyright [2025] [Mark Thomas Geleta]
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0

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
    4. `close()`: Final disposal; spellspace becomes sealed.

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
        spellspace.close()  # Fully dispose and seal the spellspace

    This system enables fast, scoped object casting with guaranteed cleanup — ideal for high-frequency or time-bound tasks.
    """
