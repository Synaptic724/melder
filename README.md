# Melder

**Melder** is a lightweight, high-performance, thread-safe Dependency Injection (DI) container built for the future of Python 3.13+ and the No-GIL era.

Designed for clarity, speed, and modular architecture —  
Melder melds your services together with minimal overhead, supporting transient, scoped, and singleton lifetimes out of the box.

Thread-safe by design, Melder enables safe concurrent service resolution across multiple threads — without sacrificing performance.

> **"Meld your services. Unify your system. Build without limits."**

---

## 🚀 Why Melder?

- ⚡ **Fast**: Built for speed and zero-dependency overhead.
- 🛠️ **Lightweight**: Small core API — easy to learn, powerful to extend.
- 🧠 **Scoping**: Support for transient, scoped, and singleton services.
- 🔍 **Observability**: (Upcoming) Built-in diagnostics and dependency graph visualization.
- 🌐 **Modern Python**: Async-compatible design planned for full coroutine support.
- 🧬 **No-GIL**: Built for the future of Python with no-GIL support.
- 🛡️ **Thread-Safe**: Designed for safe concurrent resolution across multiple threads.

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
from melder import Container

container = Container()

# Register a singleton service
class DatabaseConnection:
    ...

container.register_singleton(DatabaseConnection)

# Resolve the service
db = container.resolve(DatabaseConnection)
~~~

Scopes (planned for v0.3):

~~~
with container.create_scope() as scope:
    service = scope.resolve(DatabaseConnection)
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
