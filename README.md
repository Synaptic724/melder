# Melder

**Melder** is a lightweight, high-performance Dependency Injection (DI) container for no-gil Python 3.13+ applications.

Designed for minimal overhead, clean architecture, and simple service management —  
Melder provides core service registration, lifetime management, and resolution with a focus on speed and clarity.

> **"Meld your services, unify your system."**

---

## 🚀 Why Melder?

- ⚡ **Fast**: Built for speed and zero-dependency overhead.
- 🛠️ **Lightweight**: Small core API — easy to learn, powerful to extend.
- 🧠 **Scoping**: Support for transient, scoped, and singleton services.
- 🔍 **Observability**: (Upcoming) Built-in diagnostics and dependency graph visualization.
- 🌐 **Modern Python**: Async-compatible design planned for full coroutine support.
- 🧬 **No-GIL**: Built for the future of Python with no-GIL support.

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

Contributions are welcome!  
Please open an issue or submit a pull request to help improve Melder.

---

## 🧠 About

Melder is developed and maintained by [Mark Geleta](https://github.com/Synaptic724).  
Built for developers who value **clarity**, **performance**, and **control**.

---
