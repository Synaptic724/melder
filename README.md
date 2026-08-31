<div align="center">

# 🧙 Melder™

### The AI-Native Dependency Graph Runtime

**A runtime that an intelligence can read, inhabit, and safely change — while it's running.**

[![PyPI version](https://badge.fury.io/py/melder.svg)](https://badge.fury.io/py/melder)
[![Python Version](https://img.shields.io/pypi/pyversions/melder)](https://pypi.org/project/melder)
[![License](https://img.shields.io/github/license/Synaptic724/melder)](https://github.com/Synaptic724/melder/blob/prod/LICENSE)
[![Docs](https://readthedocs.org/projects/melder/badge/?version=latest)](https://melder.readthedocs.io/en/latest/)
[![Downloads](https://static.pepy.tech/badge/melder/month)](https://pepy.tech/projects/melder)

### SUPPORT US
If you like the work we're doing, [please give us a star on GitHub](https://github.com/meld-ai/melder).
</div>

```bash
pip install melder
```

**Zero dependencies.** Nothing else comes with it. Requires Python 3.14+.

---

## What Melder Is

Melder™ wires your application together — services, config, connections,
handlers — and hands you instances when you ask for them. That part will feel
familiar if you've used a DI container.

The difference is what happens next. **Dependency injection frameworks build
your object graph and then forget it. Melder keeps it** — as a live,
inspectable, permissioned structure you can query, snapshot, restore, and change
while the process is running.

For the one-picture distinction, open
[DI container versus Melder](architecture_and_design/05_engineering_drawings/svg/di_container_vs_melder.svg).
For the system-level view, start with
[Architecture and design](architecture_and_design/README.md).



### How it works

Three verbs. That's the entire mental model.

```
bind  →  register what exists          (classes, functions, instances)
conjure  →  compile + validate the graph   (once — cycles and gaps fail here)
meld  →  resolve instances             (as often as you like)
```

Validation happens at `conjure()`, not at first use. A cycle, a missing
provider, an ambiguous binding — you find out at startup, not at 3am.

### Who it's for

Melder scales down to a script and up to a distributed backend. Find yourself
here:

**🟢 You're writing an app and tired of passing objects around**
Four lines gets you working DI with real lifetimes and automatic teardown. No
config files, no YAML, no decorators, no base classes, and nothing new to
install. If you've been threading a database handle through five function
signatures, this is the fix.

**🟢 You want your wiring checked before you ship it**
`conjure()` compiles and validates the entire graph up front. Cycles, missing
providers, ambiguous resolutions — all surface at startup with a specific error,
not at 3am on the one code path nobody exercised.

**🟡 You're building a web service and want honest request scoping**
Per-request scopes that actually end, per-connection lifetimes, and cleanup that
fires deterministically instead of whenever the GC feels like it. Works with any
framework — Melder doesn't own your entry point.

**🟡 Your app outgrew a single container**
One registry holding everything eventually becomes its own coupling problem —
every subsystem can see every other, and one `conjure()` has to know the whole
world before it starts. Instead, give each subsystem its **own** book and
conduit: it owns its registry, exposes only what its permissions allow, and
configures and tears down independently. Link them at runtime and pull specific
spells across the boundary — `SpellContract` even lets a consumer be built
*before* its provider exists, which a single shared container can't do.

**🟠 You're running multi-tenant, plugin, or sandboxed workloads**
Aetheric frames are hard isolation walls inside one interpreter — separate
registries, separate control planes, separate singletons. One process, many
worlds, no leakage between them.

**🟠 You write tests and want real isolation**
A fresh frame per test is a fresh world. No global container to reset, no state
bleeding between cases, no ordering dependencies.

**🚀 You're doing genuinely concurrent work on 3.14+**
Lock-disciplined throughout with a documented one-way lock order, built for
free-threading rather than ported to it. Resolution never enters the transaction
plane, so concurrent reads don't contend.

**🔵 You're building agent infrastructure**
Hand an AI a permission-bounded room over a live system: it can read the graph,
work on real objects, execute validated code, preview a change's blast radius,
and hot-swap an implementation — with every structural change transacted and
reversible. See [Part II](#part-ii--the-ceiling).

**🔵 You're building a framework or platform on top**
The runtime is introspectable by design — the graph is a real structure you can
query, snapshot, restore, and extend. Melder carries its own architecture docs
inside the package so tooling can read the system without importing it.

**✨ And whatever you build, the doors are already there**
This is the part worth understanding before you start. You do not have to decide
today whether your project will ever involve AI. Build a plain application with
plain classes — and the moment you want an agent to read your architecture,
operate on live objects under a permission set, checkpoint a world, or propose a
change and be shown its blast radius, **those surfaces are already in the
runtime you're using.**

No migration. No second framework. No rewrite. Nothing to bolt on. Anything you
build with Melder can be opened up to agents whenever you're ready — because the
doors were built in from the beginning, sitting closed until you turn the handle.

### Who it's *not* for

Straight answer, so you don't waste an afternoon:

- **You need Python 3.13 or older.** Melder requires **3.14+**. That's not
  negotiable — the whole concurrency model assumes free-threading.
- **You want autowiring by magic.** Melder is explicit: you bind what exists.
  There's no classpath scanning that guesses your intent.
- **You have three objects and a `main()`.** Just construct them. A DI runtime
  earns its keep when wiring becomes a real problem, not before.

### Some of this isn't built for you

Worth saying plainly: **parts of Melder are designed for machines, not humans.**

The AR rooms, the codegen surface, the research and impact views — those are
built for an agent that can hold a whole object graph in working memory, issue
hundreds of structured queries, and act on JSON-shaped answers. A human *can*
drive them, and the API won't stop you, but you'd be hand-operating machinery
built for something with different ergonomics than yours.

That's deliberate, and it's why "AI-native" is a claim rather than a label.
These surfaces weren't retrofitted for agents after the fact — an agent is the
intended operator.

**None of it is on your critical path.** Everything in
[Part I](#part-i--the-basics) is written for humans first and stays complete on
its own. If you never open a Rift or record a checkpoint, Melder is simply a
fast, strict DI runtime and nothing is missing.

### Low floor, high ceiling

Melder is **beginner-first by design**. Four lines gets you a working graph, and
those four lines teach the whole runtime. Nothing in the advanced surface leaks into the simple
path — no mandatory configuration, no ceremony you must understand before your
first `meld()`.

But the ceiling is *very* high. The same runtime that resolves your little
service graph will checkpoint an entire distributed backend, hand an AI agent a
permission-bounded room over live objects, and track every structural change
under governance. You grow into it; it never asks you to grow into it first.

### Fast enough to not think about

Melder holds **very competitive speed** against the fastest containers in
Python — it keeps up with `dependency-injector` and `dishka`, the two names
usually at the top of that list. And it does that while carrying a full graph
runtime: validation, permissions, lifecycle tracking, and introspection that
those containers don't attempt.

For any real application, DI resolution was never your bottleneck — I/O is. What
you get for that parity is a system you can actually *see*.

### The systems layer for agentic software

The current AI tooling stack lives at the **orchestration** layer: chains,
graphs of steps, prompt routing, tool registries. Those frameworks decide *what
an agent should do next*, and they're good at it.

None of them answer the layer below. When an agent calls a tool, what is it
actually touching? Usually a loose function with no identity, no lifetime, no
ownership, no memory of having been called, and no way to undo what it did.

**Melder is that missing layer** — the low-level runtime an agent operates
*inside* rather than a bag of callables it operates *through*:

| Orchestration layer | Melder (runtime layer) |
|:---|:---|
| Picks the next step | Owns the objects the step runs against |
| Tools are functions | Objects have identity, lifetime, and an owner |
| State lives in a scratchpad | State lives in scoped, permissioned instances |
| Changes are untracked | Every structural change is recorded and reversible |
| Access is all-or-nothing | Access is a compiled permission set per room |

The two compose cleanly. Let your orchestrator decide the plan — let Melder be
the world the plan executes in, where the graph is inspectable, authority is
bounded, and every change is accounted for.

### Change as a first-class operation

Here's the part that has no equivalent elsewhere.

Most systems treat "the code changed" as something that happens *to* them —
between deploys, invisibly, with a restart to absorb it. Melder treats
structural change as an **operation the runtime performs and records**.

Versions of bound units live in lanes with forward-only history and
content-addressed identity — a unit's content hash *is* its identity, so the
same thing re-entering is recognized as a rediscovery rather than a duplicate.
Before anything changes, you can ask:

- **What's the blast radius?** — everything transitively affected
- **What drifted?** — how the running world diverges from the sealed one
- **What *would* happen?** — a read-only preview of a candidate change: the
  diff, the radius, the verdict. Nothing executes, binds, or records.

An agent can propose a structural change, be shown exactly what it would break,
and be refused — **before a single object is constructed.**

That's the difference between an AI that can *call* your system and an AI that
can safely *evolve* it.

---

## How to Read This

Every section below is tagged with the level it belongs to. **Read in order and
stop wherever you have what you need** — nothing later is required to use
anything earlier.

| | Level | What it means | Who it's for | Runnable examples |
|:--|:---|:---|:---|:---|
| 🟢 | **Beginner** | The core runtime. Bind, resolve, categorize, scope, clean up. | Everyone. Start here. | [`01_beginner/`](UX_and_AIX_experiences/01_beginner/) |
| 🟡 | **Intermediate** | Connection — module registration, dynamic linking, late binding across subsystems. | When one scope isn't enough. | [`02_intermediate/`](UX_and_AIX_experiences/02_intermediate/) |
| 🟠 | **Advanced** | Frame isolation, read-only introspection rooms, clusters, deep overrides. | Multi-tenant or multi-world systems. | [`03_advanced/`](UX_and_AIX_experiences/03_advanced/) |
| 🔵 | **Expert** | Agent rooms, transactions, checkpoints, governed mutation. Mostly machine-facing. | Building on Melder, or handing it to an AI. | [`04_expert/`](UX_and_AIX_experiences/04_expert/) |

This README is the tour. For system shape and design decisions, open
[Architecture and design](architecture_and_design/README.md); for the visual path,
start with the [engineering drawings](architecture_and_design/05_engineering_drawings/README.md).
The folders above contain runnable scripts, verified together by the
[`pytest_examples/` harness](UX_and_AIX_experiences/pytest_examples/).

**Pick a route:**

- **Evaluating Melder:** read [What Melder is](architecture_and_design/01_overview/what_melder_is.md),
  then scan the [engineering drawings](architecture_and_design/05_engineering_drawings/README.md).
- **Building an application:** enter [Part I](#part-i--the-basics), then work through
  the [`01_beginner/` examples](UX_and_AIX_experiences/01_beginner/).
- **Building runtime or agent infrastructure:** enter [Part II](#part-ii--the-ceiling),
  then continue into the [`04_expert/` examples](UX_and_AIX_experiences/04_expert/).

**If you just want dependency injection, the 🟢 sections are the entire
product.** You can stop at the end of them and never open Part II. Everything
past that point is optional capability that stays dormant until you turn it on.

---

<a id="part-i--the-basics"></a>

# Part I — The Basics

*Written for humans. Complete on its own.*

<sub>🟢 Beginner → 🟡 Intermediate → 🟠 Advanced</sub>

## 🟢 Hello, Melder
<sub>**Beginner.** The whole runtime in four lines.</sub>

```python
import melder as md


class Greeter:
    """A plain class — no base class, no metaclass, no decorator."""

    def greet(self) -> str:
        return "hello from a melded instance"


book = md.Spellbook()
book.bind(spell=Greeter, existence="unique")
conduit = book.conjure()

greeter = conduit.meld("Greeter")
print(greeter.greet())

assert conduit.meld("Greeter") is greeter   # `unique` → same instance
```

Your classes stay plain Python. Everything lives on `md.*` — if you ever need a
deep import path, that's a bug in our public surface, not a pattern to copy.

## 🟢 The Rhythm
<sub>**Beginner.** Three verbs, one order.</sub>

```python
book = md.Spellbook()

# 1. bind everything
book.bind(spell=Config, existence="unique")
book.bind(spell=Server, existence="many")

# 2. conjure ONCE  ← compiles + validates the entire graph
conduit = book.conjure()

# 3. meld everywhere
server = conduit.meld("Server")
```

**`conjure()` is where the work happens.** Requirements extraction, graph
construction, cycle detection, and runtime compilation all run there. A cycle, a
missing provider, an ambiguous resolution — it raises *there*, not at 3am when
the code path finally executes.

> **One book, one conjure.** A Spellbook produces exactly one conduit, ever.
> More scopes? `create_lesser_conduit()`. Another root? Another book.

## 🟢 The Address Law
<sub>**Beginner.** The one rule behind all resolution.</sub>

One rule governs all resolution:

> **Every spell lives at exactly one address: `(frame_key, binding_key)`**
> — `frame_key` is the `spellframe` if given, else the spell's name;
> `binding_key` is the `binding_name` if given, else the default slot.

```python
book.bind(spell=PostgresStore, existence="unique", binding_name="primary")
book.bind(spell=SqliteStore,   existence="unique", binding_name="local")

primary = conduit.meld("PostgresStore", binding_name="primary")
```

## 🟢 Spellframes — Categories Inside a World
<sub>**Beginner.** The organizing half of every address.</sub>

A `spellframe` is the **category** half of the Address Law. It can be a plain
string when you just want grouping, or a `Protocol` when you want a *shape*:

```python
# strings — organize by role
book.bind(spell=UsersRepo, existence="unique",
          spellframe="storage", binding_name="users")
book.bind(spell=UsersApi,  existence="unique",
          spellframe="web",     binding_name="users")

repo = conduit.meld(spellframe="storage", binding_name="users")
api  = conduit.meld(spellframe="web",     binding_name="users")
```

Same `binding_name`, two categories, **two distinct addresses** — names never
collide across spellframes. And because a `Protocol` works as a spellframe, one
category can mean "everything that satisfies this shape," which is exactly what
collection DI resolves:

```python
book.bind(spell=EmailHandler, existence="unique",
          spellframe=Handler, binding_name="email")
```

## 🟢 Dependency Injection
<sub>**Beginner → Intermediate.** Annotations, explicit targets, collections.</sub>

Annotate a constructor parameter. Melder builds the graph.

```python
class ReportService:
    def __init__(self, database: Database) -> None:   # ← injected
        self.database = database

book.bind(spell=Database, existence="unique")
book.bind(spell=ReportService, existence="unique")
conduit = book.conjure()

report = conduit.meld("ReportService")
```

When an annotation isn't specific enough — two implementations of one shape, or
a named binding — declare the target with `SpellMap` as the parameter default:

```python
class Consumer:
    def __init__(self, store=md.SpellMap(PrimaryStore)) -> None:
        self.store = store
```

`SpellMap` takes the full address: a concrete spell, a `spellframe`, a
`binding_name`, or a combination. It obeys an **exactly-one law** — a target
that matches zero spells or several fails at `conjure()`, not at runtime.

Ask for a list and get every implementation — the plugin pattern in one
annotation:

```python
class Dispatcher:
    def __init__(self, handlers: list[Handler]) -> None:   # ← all of them
        self.handlers = handlers

book.bind(spell=EmailHandler, existence="unique",
          spellframe=Handler, binding_name="email")
book.bind(spell=SmsHandler, existence="unique",
          spellframe=Handler, binding_name="sms")
```

## 🟢 Six Lifetimes, Not Three
<sub>**Beginner.** Pick how long things live.</sub>

| | Existence | One instance per | Use it for |
|:--|:---|:---|:---|
| 🟢 | `unique` | Process (frame) | Config, pools, caches |
| 🟢 | `unique_per_conduit` | Scope | Request / session state |
| 🟢 | `many` | Nothing — new every meld | Stateless workers, DTOs |
| 🟡 | `unique_per_conduit_lineage` | A scope **and its children** | Shared context down a tree |
| 🟡 | `unique_per_spell_space` | A request-local space | Ephemeral request scoping |
| 🟠 | `unique_per_conduit_cluster` | A named group of scopes | Cross-scope coordination |

**The first three are the beginner set** — they cover most systems and need
nothing but a static conjure. The last three arrive with the features that give
them meaning: lineage and spell spaces once you have nested scopes, clusters
once conduits link into groups.

> Callables are always `unique`. Want a fresh object every time? Bind a **class**
> as `many`.

## 🟢 Teardown Is Part of Registration
<sub>**Beginner.** Cleanup without ceremony.</sub>

Declare your teardown **vocabulary** — the method names that mean "clean
yourself up" in this system — and Melder calls them on the way down. No base
class, no protocol, no context-manager ceremony:

```python
book = md.Spellbook()

book.bind(
    spell=PooledConnection,
    existence="unique",
    disposal_method_names=["close", "shutdown"],   # ← the book's vocabulary
)
book.bind(spell=BackgroundWorker, existence="unique")

conduit = book.conjure()
...
conduit.cleanup()     # → close() on the connection, shutdown() on the worker
```

The vocabulary is **book-wide and set once** — the first bind that supplies it
fixes it (you can also set it on `SpellbookConfiguration`). Each spell then
resolves to the intersection of that vocabulary and the methods it actually
has:

- `PooledConnection.close()` exists → it gets called
- `BackgroundWorker.shutdown()` exists → it gets called
- A class with neither → carries no disposal metadata and costs nothing

Teardown is **best-effort and complete**: every object is attempted, and any
failures are aggregated into a single `ExceptionGroup` rather than the first
error aborting the rest of your cleanup.

## 🟢 Scopes That Nest
<sub>**Beginner.** Child scopes, no configuration.</sub>

```python
root = book.conjure()
child = root.create_lesser_conduit()

assert root.meld("Config") is child.meld("Config")      # shared
assert root.meld("Session") is not child.meld("Session") # per-scope
```
## 🟡 Declarative Binding by Module
<sub>**Intermediate.** Register where the class lives.</sub>

Prefer to declare registration where the class lives? Tag it with
`@md.scan_bind`, then register the whole module in one call.

**`services.py`** — declare intent next to the code:

```python
import melder as md


@md.scan_bind(existence="unique")
class MetricsHub:
    pass


@md.scan_bind(existence="many")
class JobTicket:
    pass
```

**`main.py`** — decide when it actually binds:

```python
import melder as md
import services

book = md.Spellbook()
bound = book.scan(services)        # ← binds every tagged class in the module
conduit = book.conjure()

hub = conduit.meld("MetricsHub")
```

The decorator **stores intent only** — nothing touches the runtime until
`scan()` runs. Importing `services` registers nothing: no hidden global
container filling up behind your back, no import-order puzzle to debug. You
still decide when binding happens, and where.

Mix freely: scan a module, then `bind()` a few more by hand.


---

## 🟡 Dynamic Mode & Linking Conduits
<sub>**Intermediate.** Everything above works without this. Turn it on when
separate parts of your system need to share.</sub>

By default a world is **static** — bind, conjure, resolve. Turn on dynamic mode
and conduits gain the ability to connect to each other at runtime.

The mode is decided **once, by the first conjure**, and then inherited:

```python
# SETTLEMENT — the first conjure on a fresh world sets the mode, and it locks
owner = owner_book.conjure(dynamic=True, name="owner")

# INHERITANCE — later books just attach; a plain conjure() inherits the mode.
# You never repeat the flag.
borrower = borrower_book.conjure(name="borrower")
```

Now link them and share a spell across the boundary:

```python
owner.link(borrower)                       # open a contract between the two

borrower.add_spell_to_contract(            # ← the BORROWER asks
    spell_id=spell_id,
    conduit=owner,                         # ← from the conduit that OWNS it
    permissions="create",
)

shared = borrower.meld("SharedDirectory")   # resolves the owner's spell
```

**Sharing is a pull, never a push.** The conduit that wants the spell asks for
it, and names the owner. An owner cannot force its objects into someone else's
scope — so nothing arrives in your conduit that you didn't request.

## 🟡 Late Binding with `SpellContract`
<sub>**Intermediate.** Wire whole subsystems together without either side
importing the other.</sub>

A `SpellContract` is a **hole you leave on purpose**. The class declares the
*shape* it needs; the provider arrives later, across a link:

```python
class ReportService:
    def __init__(
        self,
        config: ConfigContract = md.SpellContract(
            spellframe=ConfigContract, binding_name="platform",
        ),
    ) -> None:
        self.config = config        # ← filled from another conduit entirely
```

Name your conduits after the resolution ideas your app already has — `platform`,
`services`, `workflows` — and the conduit names *become* your factory layer. No
abstract factories, no service locator, no imports between subsystems.

**The order of operations is the law.** Per dependency edge, in this exact
order:

```python
platform = platform_book.conjure(dynamic=True, name="platform")  # 1. provider
services = services_book.conjure(dynamic=True, name="services")  # 2. consumer
platform.link(services)                                          # 3. link — AFTER both exist
services.add_spell_to_contract(                                  # 4. consumer pulls
    spell_id=config_id, conduit=platform, permissions="create",
)
service = services.meld(spell_id=service_id)                    # 5. meld completes the binding
```

Assemble the chain edge by edge, in dependency order. `services` can then feed
`workflows` with the identical five steps one level up — the finished product of
one category becomes the dependency of the next.

## 🟠 Frame Boundaries — More Than One World Per Process
<sub>**Advanced.** Hard isolation walls inside a single interpreter.</sub>

Everything so far has lived in one **aetheric frame** — the default world. A
frame is the outermost boundary in Melder: it owns its own conduits, registries,
control plane, and dynamic posture. Name a different one and you get a second
world that shares nothing with the first:

```python
tenant_a = md.Spellbook(aetheric_frame="tenant-a")
tenant_b = md.Spellbook(aetheric_frame="tenant-b")
```

Both can bind the same class under the same name with zero collision, and a
`unique` spell is a singleton **per frame** — not per process. Two frames, two
instances, one interpreter.

That makes frames the natural seam for multi-tenancy, plugin isolation, and test
isolation (a fresh frame per test is a fresh world). Conduits link *within* a
frame; they do not link across one — the wall is real.

> Don't confuse the two "frames": `spellframe=` is an **address key** that
> categorizes spells *inside* a world. `aetheric_frame=` is the **world itself**.

### Three widths of category

Once you see it, the same idea repeats at three scales — each one a wider
boundary than the last:

| Scale | Categorizes | Owner |
|:---|:---|:---|
| **`spellframe`** | Spells *within* one world | The book that bound them |
| **Conduit** | Worlds of resolution, linked by contract | Each conduit owns its category |
| **`aetheric_frame`** | Entire isolated worlds | The frame itself |

Pick the narrowest one that expresses what you mean. Most systems need only the
first; large ones grow into the second; the third is for genuine isolation.

## 🟠 Read-Only Rooms for Endpoints
<sub>**Advanced.** A safe window onto a running system — no agent required.</sub>

You don't need to be building AI to want a live view of your own runtime. A
`static` Nexus room is exactly that: a read-only projection over a running frame
that can inspect everything and change nothing.

That makes it a natural backing for the introspection surfaces you'd otherwise
hand-roll:

- a **health endpoint** that reports what's genuinely live, not what you hope is
- an **admin panel** listing resolved services and their scopes
- a **debug view** of the real dependency graph in production

Because the room's authority is compiled and read-only, exposing it carries no
mutation risk — the worst a caller can do is look. The `capability` and
`codegen` rooms in [Part II](#part-ii--the-ceiling) escalate from here.

### What else this README skips

Real surfaces this page doesn't walk through — all covered in the
[documentation](#documentation):

| | Surface | What it does |
|:--|:---|:---|
| 🟡 | **Spell spaces** | Request-local scopes backing `unique_per_spell_space` |
| 🟡 | **Registration hooks** | pre / activation / post callbacks on the bind lifecycle |
| 🟡 | **`SpellBinder`** | A fluent chained alternative to `bind(...)` |
| 🟡 | **Ownership transfer** | Move a spell's stewardship between conduits at runtime, repointing borrowers and clusters |
| 🟠 | **Conduit clusters** | A named group of scopes sharing one instance, with an elected leader |
| 🟠 | **Deep override paths** | Inject a variant into the *middle* of a live graph at meld time — `override={"transport>credentials": obj}` — without rebinding anything |

---

<a id="part-ii--the-ceiling"></a>

# Part II — The Ceiling

*Mostly written for agents. Optional, and off unless you turn it on.*
Everything above is a very good DI container. This is why Melder exists.

> **A note on the audience.** The surfaces below assume an operator that reads
> structured output fast and issues many precise calls — an agent, in other
> words. They're documented here so you know the ceiling exists and can reason
> about what you're handing an agent. You are not expected to drive them by
> hand, and nothing in Part I depends on any of it.

## 🔵 The Runtime Documents Itself
<sub>**Expert / agent-facing.** The package carries its own architecture.</sub>

Melder ships its own architecture as queryable objects **inside the wheel**. An
agent reads the system before touching it — no web, no scraping, no RAG:

```python
import melder as md

md.__architecture__     # system architecture (C4)
md.__components__       # component catalog
md.__graph_network__    # object relationship graph
md.__graph_details__    # detailed wiring

help(md)                # the workflow map
```

Most frameworks make an agent guess from source. Melder hands it the map.

## 🔵 Give an Agent a Room, Not Your Process
<sub>**Expert / agent-facing.** Bounded authority over a live frame.</sub>

`Nexus` is the mediated access layer into the live object world. You open a
**Rift** — a workspace over a running frame — and the room decides how much
authority the occupant has.

```python
rift = nexus.create_rift(rift_name="alpha")
conduit = rift.create_nexus_frame(frame_name="ops")   # rooted, live
```

Three room postures, escalating:

| Room | What the occupant can do |
|:---|:---|
| `static` | Read-only. Inspect live spells, never mutate topology. |
| `capability` | Discover conduits, traverse contracts, activate spells, mutate topology. |
| `codegen` | Everything above **plus write and execute Python against live objects**. |

`static` is covered back in [Part I](#-read-only-rooms-for-endpoints) — it needs
no agent and works fine as a plain introspection endpoint. The two below are
where authority starts escalating.

### The agent's seat

Open a room over a live frame, and it comes with a workbench attached:

```python
rift = nexus.create_rift(rift_name="alpha")
root = rift.create_nexus_frame(frame_name="ops")   # a real, rooted conduit
rift.create_frame_link("ops")

space       = rift.space              # the room
viewer      = space.frame_viewer      # read the live graph
workstation = space.workstation       # a bench to put objects on
command     = space.command_system    # the room's verbs
```

The **workstation** is where an agent keeps what it's working on — bind a live
object to a name, make it the active target, then operate on it:

```python
service = root.meld("ReportService")

workstation.bind_object("svc", service)   # park a LIVE object on the bench
workstation.set_target("svc")             # make it the active target
workstation.call_target()                 # ...and drive it
```

Then the agent writes Python against that world. The generated code runs in a
namespace you compiled — these five names and nothing else:

```python
code = """
# viewer / workstation / target / command / codegen — the whole namespace

frames  = viewer.list_nexus_frame_names()   # read the live world
current = target                            # the bench's active object
result  = {"frames": frames, "kind": type(current).__name__}
"""

outcome = command.execute_codegen(code, frame_name="ops")
# every fragment is VALIDATED before it runs; a rejected one never executes
```

The agent inspects the running system, works on real objects, and writes code
against them — without ever holding a reference to your process.

And the ACL is a **dial**, compiled per frame:

```python
imports_enabled          = False        # no imports at all
allowed_import_module_roots = ("json",) # ...or exactly these
denied_builtin_names     = ("eval",)    # kill specific builtins
unsafe_reflection_allowed = False       # no type()/introspection escapes
dunder_access_allowed    = False        # no __class__ walks
recursive_codegen_allowed = False       # code that writes code
```

Every generated fragment is **validated before it executes**. `import math` in a
json-only room is rejected. `type(command)` in a reflection-denied room is
rejected. The agent gets a real seat at the runtime, bounded by a permission set
you wrote.

## 🔵 An Internal DevOps Plane, With Real Transactions
<sub>**Expert.** How concurrent structural change stays safe.</sub>

The obvious question about everything above: *if an agent can rewire my topology
while the system is running, what stops it corrupting the world?*

Melder carries a full **internal DevOps environment** — a control plane that
admits, serializes, and audits every structural change. It isn't a lock around
the container. It's a transaction system with **ACID semantics** over the
object graph.

Every structural mutation is a **transaction** in a named family:

```
bind · link · unlink · cluster_link · transfer_ownership
add_to_index · remove_from_index · notch
```

Each one declares the scopes it touches and the *mode* it needs, then a mediator
admits it — or makes it wait.

**Atomicity** — Scope acquisition is all-or-nothing. A request takes every scope
it needs or none of them, and owns exactly one root session. Failures compensate:
a refused operation rolls back its claims, and a mid-operation refusal restores
everything it had already moved, in original order.

**Consistency** — Changes propagate as invalidation, not corruption. Touching a
lineage marks dependents dirty; the resolver refuses to execute a stale graph and
recompiles it first. A built-in consistency audit walks every bidirectional map
looking for asymmetry — any mismatch is evidence a write bypassed the plane.

**Isolation** — Claims are *moded*, not binary: `x` exclusive, `s` shared, `ix`
intent. Disjoint work admits in parallel; shared and intent claims coexist on the
same scope; exclusive excludes everything. Two subsystems binding into different
books never see each other. Two operations targeting the same conduit serialize.
Waiting is bounded, and a timeout names **which scope blocked and who held it** —
not a generic deadlock.

**Durability** — Committed structure is recorded to the persistence twin and
survives into checkpoints (next section).

Two design choices worth calling out:

- **Readers never enter the plane.** `meld()` doesn't take transaction locks —
  resolution stays fast and is protected by validity gating instead. You pay for
  coordination only when you *change* something.
- **Ownership is asymmetric on purpose.** Sharing is a *pull*: the conduit
  requesting a spell must be the one that gets it, and an owner cannot push its
  objects into someone else's scope.

There's also a queryable operations catalog — live transaction activity, cluster
fan-out, the blast radius of a proposed ownership transfer, a whole-frame
operational rollup, and that registry consistency audit. It's caller-paid: nothing
runs it for you, and it costs nothing until asked.

### This is what everything else stands on

The DevOps plane isn't a side feature — it's the reason the rest of this README
is safe to promise. Every capability above and below runs *through* it:

| Capability | What the plane guarantees |
|:---|:---|
| 🟡 **Linking conduits** | `link` / `unlink` are transactions. Two subsystems wiring themselves simultaneously serialize on the shared scopes and proceed in parallel everywhere else. |
| 🔵 **Hot-swapping a live spell** | `notch` is a transaction. The index repoint, the parking of the old version, and dependent invalidation land atomically — a meld never observes a half-swapped index. |
| 🔵 **Agents mutating topology** | Generated code has no privileged path. `command.link_frame(...)` from a codegen room enters the same plane, takes the same claims, and waits like anything else. |
| 🔵 **Checkpoints** | Only committed structure is recorded. A checkpoint can't capture a half-applied transfer, so a restored world is one that actually existed. |
| 🚀 **Parallel everything** | Moded claims mean disjoint work never contends. This is what makes concurrent structural change *fast* rather than merely *survivable*. |

Take the plane away and every one of those becomes a race condition. That's why
it's here, and why an agent gets to touch a live system at all.

## 🔵 Checkpoint the World, Rebuild It Cold
<sub>**Expert.** Persistence, cold boot, and pod restarts.</sub>

`Crystallizer` records a **digital twin** of your configured system — structure,
never live instances:

```python
checkpoint_id = crystallizer.create_checkpoint(description="pre-migration")

crystallizer.describe_profile()               # what's recorded right now
crystallizer.describe_checkpoint(checkpoint_id)
```

Restore replays that world **through public verbs only** — the same `bind`,
`conjure`, `link` calls you would have written. Which means:

- **Fresh identities always.** ULIDs are minted new, never rehydrated.
- **All-or-nothing.** Any stage failure tears down everything in reverse order.
- **An honest ledger.** Anything unreplayable is a *named shortfall*, never a
  silent gap.
- **Drift detection.** Every load re-hashes your source against the sealed
  fingerprint and announces divergence before building anything.

### Saving is half of it — loading is the point

A checkpoint you can't boot from is a diary. `CrystallizerBootstrap` is the
other half: **one fluent chain that brings an entire world back on a cold
process.**

```python
report = (
    CrystallizerBootstrap()
    .with_external_persistence_manager(          # optional: your own DB
        ExternalPersistenceManagerConfiguration()
        .with_upload_handler(upload)
        .with_download_handler(download)
        .with_list_handler(list_ids)
    )
    .with_profile("default")
    .bootstrap()
)

report["activated"]              # crystallizer live
report["remote_reload"]          # what was pulled back from your store
report["restored_checkpoint_id"] # which world it booted
report["restore_report"]         # per-stage build counts + shortfalls
```

That single chain does the whole cold start: activate → attach your storage →
reload the local cache → pull from remote and re-flush it locally → verify the
checkpoint chain → restore the newest world → hand you a report.

**Storage is yours.** Melder ships no database driver and no cloud SDK. You
hand it four callables — store, fetch, list, delete — and it uses them. Your
Postgres, your S3, your Redis, your rules. That's why the dependency list is
empty.

A pod restarts, pulls its last checkpoint, and rebuilds the world structurally
intact — no serialized objects, no pickle, no version-brittle blobs. The spell
identity that comes back is the *same content hash* that went in.

## 🔵 Structural Change, Under Governance
<sub>**Expert / agent-facing.** Hot-swap a live implementation, with foresight and rollback.</sub>

This is where "hot reload" stops being a figure of speech. An agent can swap a
live implementation for a new one on a running system — but first it has to
answer the only question that matters: **what does this break?**

```python
research = conduit.mutation_research     # the world's research record

# 1. WHAT IS THIS THING NOW? — declared lane, live state, stored custody
research.residency_view(spell_id)

# 2. WHAT DOES IT COST TO TOUCH IT? — transitive blast radius,
#    joined with which lanes and campaigns those spells live in
research.impact_view(spell_id=spell_id)

# 3. WHAT *WOULD* HAPPEN? — the read-only rehearsal
candidate = """
class ReportService:
    def run(self) -> str:
        return "v2 report"
"""
verdict = research.preview_candidate(candidate, against_spell_id=spell_id)
# → what it defines, what it imports, how it differs from the version it
#   would replace, and the radius that replacement would carry.
#   NOTHING executes, binds, or records. It is a rehearsal, not a change.
```

### Then it actually changes the thing

Foresight is half of it. The other half is the live swap — **stage → notch →
meld**, on a running system, with the old version still sitting there:

```python
# 1. STAGE — bind a new version as an INACTIVE member of the existing index.
#    It is parked and unresolvable: nothing melds it, nothing sees it yet.
id_v2 = conduit.bind_inactive(
    spell=ReportServiceV2,
    spell_index=index,          # the index the current version lives in
    existence="unique",
    binding_name="v2",
)

# 2. NOTCH — promote v2 to ACTIVE. The outgoing version parks, the index
#    pointer repoints, and dependents are marked for lazy recompile.
conduit.notch_spell(spell_index=index, spell=spell_v2)
assert index.selected_spell_id == id_v2

# 3. MELD — the very next resolution builds the NEW version.
service = conduit.meld(spell_id=id_v2)   # → ReportServiceV2
```

And because the old member is **parked, not destroyed**, rollback is the same
verb pointed the other way:

```python
conduit.notch_spell(spell_index=index, spell=spell_v1)   # instant revert
```

> **The parked version is still in the ecosystem.** Notching does not dispose of
> anything — v1 remains a member of the index, holding its slot and its state.
> That's what makes the revert above instant, but it also means **retirement is
> a deliberate act**: the agent (or you) decides when a version leaves, and
> removes it explicitly. Nothing is swept up for you, and nothing disappears
> behind your back.

That's the whole loop: an agent reads the system, previews a change, stages it
beside the live one, promotes it, and can put it back — while the process keeps
running. Every world entry and promotion lands in a journal you can walk, in
**lanes** with forward-only history and content-addressed identity (a unit's
content hash *is* its identity, so the same code re-entering is a rediscovery,
not a duplicate).

The point isn't that an agent *can* mutate your system. It's that it's shown the
cost first, the change is staged rather than smashed in, and the previous
version is one call away.

## 🚀 All of It, in Real Parallel
<sub>**Everyone.** Free-threading is the foundation, not a feature.</sub>

Every DI library in Python was designed when threads couldn't run
simultaneously. "Thread-safe" meant "we put a mutex on it," because contention
was theoretical.

Melder was written after that stopped being true.

- Lock-disciplined registries and scopes with a **documented one-way lock order**
- Concurrent resolution as a **first-class path**, not a footnote
- Real threads, real shared memory — **no multiprocessing crutches**
- Warns at import if it detects a **GIL-enabled** build

### Two planes, on purpose

The reason Melder can be *both* fast and safe under real parallelism is that
reads and writes don't share a road:

| | Readers — `meld()` | Writers — structural change |
|:---|:---|:---|
| **Path** | Never enter the transaction plane | Admitted through the mediator |
| **Protection** | Validity gating: a stale graph is refused and recompiled | Moded scope claims (`x` / `s` / `ix`) |
| **Contention** | None with other readers | Only with work touching the same scopes |
| **Cost** | Resolution speed, uncompromised | Paid once, at the moment you change something |

Resolution — the thing you do thousands of times — carries no transaction
overhead at all. Coordination is charged only to the thing you do rarely:
changing the shape of the system.

That split is what makes the whole design hold together. Without free-threading
there'd be no real parallelism to protect. Without the mediator, parallel
structural change would be a race. You need both, and Melder was built assuming
both from the first line.

---

## Documentation

Use the routes below to choose source-controlled architecture, runnable examples,
hosted reference, or video walkthroughs. This README stays the runnable tour;
long-form guides and API reference belong in the hosted documentation site.

| | Where | What's there |
|:--|:---|:---|
| 🗺️ | **[Architecture and design](architecture_and_design/README.md)** | High-level pictures, runtime structure, utilization stories, and tradeoffs |
| 🖼️ | **[Engineering drawings](architecture_and_design/05_engineering_drawings/README.md)** | DI comparison, C4/C3/C2 views, use cases, lifecycle, coordination, recovery, and advanced flows |
| 🧪 | **[Runnable examples](UX_and_AIX_experiences/)** | Beginner-to-expert scripts organized by the same level ladder used in this README |
| ✅ | **[Example verification](UX_and_AIX_experiences/pytest_examples/)** | Pytest harness and contract probes for the runnable curriculum |
| 📘 | **[Getting started](https://www.synapticaisystems.com/melder/intro/)** | The guided introduction — start here after this page |
| 📚 | **[melder.readthedocs.io](https://melder.readthedocs.io/en/latest/)** | Full API reference and technical documentation |
| ▶️ | **[Synaptic AI on YouTube](https://www.youtube.com/@SynapticAISystems)** | Walkthroughs, deep dives, and live builds |

## License

GNU Affero General Public License v3.0 or later (AGPL-3.0-or-later) — see [LICENSE](LICENSE).

The AGPL's network clause applies: if you run a modified version of Melder™ as a
service that users interact with over a network, you must offer those users the
corresponding source of your modified version.

**Trademark.** Melder™ is a trademark of Mark Thomas Geleta / Synaptic AI
Systems. The AGPL grants rights in the software, not in the name — forks and
redistributions must not use the Melder name or marks in a way that suggests
endorsement by, or origin from, the trademark holder. See [NOTICE](NOTICE).

## Contributing

Issues and design discussion welcome via
[GitHub issues](https://github.com/Synaptic724/melder/issues).

Melder is under active architectural development — if you're planning something
substantial, open an issue first so we can align on direction.

---

<div align="center">

Built by **[Mark Geleta](https://github.com/Synaptic724)** · Synaptic AI Systems

<sub>A better place for intelligence to live and work.</sub>

</div>
