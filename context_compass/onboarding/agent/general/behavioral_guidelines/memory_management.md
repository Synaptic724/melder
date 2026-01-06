# memory_management

Purpose
- Describe how agents use user and system memory stores.

Story steps
1) Determine whether memory is needed
   - User memory: only write when the user explicitly asks.
   - System memory: write when capturing operational facts.

2) Read memory explicitly
   - Use memory_read before relying on stored facts.
   - Treat entries as advisory.

3) Write or update memory
   - Use memory_add or memory_update with clear titles and tags.
   - Avoid secrets and sensitive data.

4) Remove stale memory
   - Use memory_remove to delete entries outright.

Artifacts
- context_compass/system/memory/user_memory.json
- context_compass/system/memory/system_memory.json

Tools
- context_compass/system/ai_restricted/memory/memory_add.py
- context_compass/system/ai_restricted/memory/memory_update.py
- context_compass/system/ai_restricted/memory/memory_remove.py
- context_compass/system/ai_restricted/memory/memory_read.py
