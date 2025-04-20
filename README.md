Melder is a next-generation, lightweight, high-performance, thread-safe system for Dependency Injection (DI) and Modular Scoped Execution — built for the future of Python 3.13+ and the no-GIL era.

Melder doesn’t just inject dependencies.  
It **builds dynamic, permissioned, scoped execution graphs**, enabling services to resolve, interact, and scale cleanly — without rigid factory bloat, fragile wiring, or hidden coupling.

Designed for **clarity**, **modularity**, and **speed**,  
Melder melds your services together with minimal overhead — supporting transient, scoped, and singleton lifetimes with true lifecycle management.

Built for serious architectures, Melder is **thread-safe by design**, enabling safe concurrent service resolution across multiple threads without sacrificing performance — and ready to thrive in Python’s new free-threading world.

> **"Meld your services. Forge your system. Awaken your inner digital sorcerer."**

Melder is not just another helper library.  
Melder solves Dependency Injection’s problems by evolving it into scoped dynamic modular execution — without losing its soul.

---

## 🧠 Why Use a Dependency Injection Container?

Using a Dependency Injection (DI) container like Melder provides deep structural advantages:

- 🧩 **Loose Coupling**  
  DI allows components to depend on *abstractions* rather than *concrete implementations*, making your codebase modular, flexible, and easier to evolve.

- 🔁 **Circular Reference Management**  
  Complex interdependent services (like database handlers, background workers, API clients) are easier to construct without getting trapped in manual wiring or circular import nightmares.

- 🧹 **Centralized Object Management**  
  By controlling service lifetimes (singleton, scoped, transient) through the container, you eliminate the hidden mess of manually constructed objects sprinkled across the app.

- 🛠️ **Cleaner Architecture**  
  Services are automatically composed and injected where needed — no more "global variables" or fragile manual dependency wiring.

- 🗂️ **Dependency Traceability**  
  You know exactly what depends on what, because it's all wired through a single, auditable registration process.

- 🚮 **Better Resource Cleanup**  
  Scoped services can be automatically disposed of when the scope ends, helping manage memory, close connections, and release resources cleanly.

- ⚡ **Faster Changes, Less Risk**  
  Need to swap a database backend, or inject a mock service for testing?  
  Update the container bindings — no need to touch dozens of files.

- 🌱 **Scales With Your Codebase**  
  Whether you're managing 5 services or 500, a DI container helps you scale cleanly without losing track of your architecture.

---

## 🧱 Philosophy: No More Technical Debt

With the removal of Python's greatest technical debt — the Global Interpreter Lock (GIL) —  
there are no more excuses.

**Melder is not just another helper library.**  
It is a foundation for serious Python systems built for the no-GIL, fully concurrent future.

For decades, Python survived without true Dependency Injection because it could get away with it:  
- Scripts were small.  
- Services were short-lived.  
- Single-threaded execution papered over architecture flaws.
- Tools like multiprocessing as a crutch

**But those days are over. It's time to move forward**

Python 3.13+ introduces true multithreading, unlocking possibilities the language has never seriously supported before.  
**The lack of real, thread-safe service containers is no longer tolerable.**  
Systems will scale wider, codebases will grow larger, and architectural discipline will become mandatory.

Melder is designed for **projects of any size**:
- From small apps with a handful of services,
- To massive architectures with **millions of lines of code**,
- To high-concurrency systems where thread-safety, lifetime management, and composability are not optional — they are survival.

No more duct tape.  
No more hard-coded spaghetti.  
No more "just pass the config around" hacks.

We are building **the future of Python** —  
**modular, fast, clear, and built to last.**

---



## 🚀 Why Melder?

- ⚡ **Fast**: Built for speed and zero-dependency overhead — no slow reflection hacks or runtime magic.
- 🛠️ **Lightweight**: Small, surgical core — easy to learn, powerful to extend without pulling in massive frameworks.
- 🧠 **True Scoping**: Full support for transient, scoped, and singleton services — with real scope boundaries, not faked with globals.
- 🔍 **Observability** *(Upcoming)*: Built-in diagnostics and dependency graph visualization — making your architecture visible, not invisible.
- 🌐 **Modern Python**: Designed for Python 3.13+ and fully compatible with the new concurrency era.
- 🧬 **No-GIL Ready**: Engineered to thrive in Python’s new free-threading world — no multiprocessing crutches needed.
- 🛡️ **Thread-Safe by Design**: Safe concurrent resolution across threads — not an afterthought, but a first-class feature.
- 🧠 **Explicit, Not Magical** *(Maybe...)*: No hidden behavior. No auto-wiring messes. You control what gets built and how.
- 🧠 **System Architecture First**: Melder isn't just about convenience — it's about forging scalable, maintainable, high-concurrency systems.

---

## 📦 Installation

Coming soon after initial release.

Once published, you will be able to install Melder via pip:

~~~
pip install melder
~~~

---

## ✨ Quickstart Example

Register services and resolve them easily:

~~~
from melder import spellbook

spellbook = spellbook()

# Register a singleton service
class DatabaseConnection:
    ...

spellbook.bind(DatabaseConnection, existence='unique')

# Resolve the service
db = spellbook.meld(DatabaseConnection)
~~~

Scopes (planned for v0.3):

~~~
with spellbook.conduit() as conduit:
    service = conduit.meld(DatabaseConnection)
~~~

---

## 📚 Planned Features

- [x] Singleton, Transient, and Scoped lifetimes
- [x] Factory-based registrations
- [ ] Constructor injection (auto-resolve init arguments)
- [ ] Lazy service resolution
- [ ] Dependency graph visualization
- [ ] Async service resolution
- [ ] Diagnostics and profiling

See the full [Roadmap](ROADMAP.md) for detailed version milestones.

---

## 🛤 Roadmap

| Version | Focus |
|:---|:---|
| v0.1 | Basic registration and resolution |
| v0.2 | Factories and instance binding |
| v0.3 | Scoping support |
| v0.4 | Advanced cleanup and disposal |
| v0.5 | Decorators and helper utilities |
| v0.6 | Dependency graphs and visualization |
| v0.7 | Constructor injection and multiple resolutions |
| v0.8 | Async support |
| v0.9 | Diagnostics and profiling |
| v1.0 | Full production release |

---

## 📖 Documentation

- Coming soon: [Melder Documentation](https://github.com/Synaptic724/melder)

---

## 📝 License

Melder is licensed under the [Apache 2.0 License](LICENSE).

---

## 🤝 Contributing

Melder is currently developed as a **solo project** and is **not open to external contributions** at this time.

Bug reports and feature suggestions are welcome via [issues](https://github.com/Synaptic724/melder/issues),  
but pull requests will not be accepted.

Thank you for respecting the creative direction of the project.

---

## 🧠 About

Melder is developed and maintained by [Mark Geleta](https://github.com/Synaptic724).  
Built for developers who value **clarity**, **performance**, and **control**.

---
