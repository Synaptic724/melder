# ✨ Melder Advanced Scopes (Future Plans)

Melder currently supports:

- **Global existence** (Spellbook container-wide)
- **Conduit existence** (per conduit)
- **Many existences** (transient)

---

## 🛠️ Planned Scope Types

| Scope Type                | Description                                              | Purpose                                               |
|----------------------------|----------------------------------------------------------|-------------------------------------------------------|
| Named Conduits             | Conduits that can be explicitly named and retrieved later. | Track specific sessions, users, transactions.         |
| Thread-Scoped Conduits     | One existence per operating system thread.               | Thread-local storage patterns.                        |
| Async Task-Scoped Conduits | One existence per coroutine context (`asyncio.Task`).     | Web servers, event-driven apps, request isolation.     |
| Time-Bound Conduits        | Conduits that automatically seal themselves after a timer expires. | Expiring sessions, cache lifetimes, auto-cleanup.     |
| Externally-Owned Conduits  | Conduits tied to external lifecycle events.               | Automatic disposal after HTTP request, worker job, etc.|
| Weakref-Based Existences   | Services that exist only if referenced elsewhere.         | Extreme memory optimization patterns.                 |

---

## 🧠 Tactical Future Usage

Examples of how these could look:

~~~
# Named conduit
with spellbook.create_conduit(name="user-session-abc") as conduit:
    service = conduit.meld(MyService)

# Thread-local conduit
conduit = spellbook.create_thread_conduit()

# Async task-local conduit
conduit = await spellbook.create_task_conduit()

# Time-limited conduit (auto-seals after 30 seconds)
with spellbook.create_conduit(timeout=30) as conduit:
    service = conduit.meld(RequestHandler)

# Weakref existence
spellbook.bind(CacheEntry, existence="weak")
~~~

---

## 🚀 Why Add Advanced Scopes?

- Fine-grained control over service lifetime and memory.
- Build ultra-scalable web backends, microservices, and high-concurrency systems.
- Native integration potential with frameworks like FastAPI, Starlette, Django async views, etc.
- Become the default DI system for serious Python 3.13+ multithreading and No-GIL applications.
- Unlock new debugging, optimization, and architecture possibilities.
