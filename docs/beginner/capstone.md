# Build a complete beginner application

Build a small orders application with ordinary Python objects, one bootstrap,
and a separate module that uses the running graph. The configuration and pool
are shared; each request receives a fresh handler.

## Give each module one job

Keep these four files together in the saved Beginner collection:

```text
01_beginner/
├── capstone_models.py        # Your application objects
├── capstone_bootstrap.py     # Register objects and conjure once
├── capstone_application.py   # Resolve typed objects and use them
└── 40_beginner_capstone.py   # Start, run, and clean up
```

The entry point calls the bootstrap, passes the returned conduit to the
application, and owns shutdown. The application module receives a usable
conduit and works with the objects returned by `meld()`.

All four modules run in one Python process. Importing `capstone_bootstrap`
loads the `build_application` function definition. The graph is created when
`main()` calls that function:

1. `build_application()` creates the book, binds the classes, conjures, and returns both objects.
2. `main()` receives them in `book, conduit`.
3. `run_application(conduit)` passes that same conduit object into the application function.
4. The function uses its `conduit` parameter to resolve application objects.
5. When it returns, `main()` owns shutdown.

## Define ordinary application objects

`capstone_models.py` contains configuration, a small resource, and a request
handler. `DbPool` uses an in-memory order store to demonstrate a pool's lifetime;
it opens no database connection. The handler uses its injected configuration
and pool to answer a request.

The constructor's `AppConfig` and `DbPool` annotations refer to real classes
available in this module. Melder can inspect those dependencies when building
the handler. The handler borrows the pool; the conduit owns its disposal.

```{literalinclude} ../downloads/01_beginner/capstone_models.py
:language: python
:caption: capstone_models.py
```

## Bootstrap with direct binding calls

The bootstrap imports the actual classes, registers them, and conjures once.
Each `bind()` manages its own transaction and synchronization. Ordinary binding
needs no outer `with book:` block; these are individual registration calls.

| Registration | Lifetime | Result |
| --- | --- | --- |
| The `AppConfig` class | `unique` | Every handler receives one shared configuration object |
| The `DbPool` class | `unique` | All requests share one pool; cleanup calls `close()` |
| The `RequestHandler` class | `many` | Every meld creates a fresh handler with injected dependencies |

The configuration uses its ordinary Python constructor default. The bootstrap
registers its class, and Melder creates the shared object when it is first resolved.

```{literalinclude} ../downloads/01_beginner/capstone_bootstrap.py
:language: python
:caption: capstone_bootstrap.py
```

## Resolve typed objects in the consuming module

This consumer uses `md`, `AppConfig`, `DbPool`, and `RequestHandler` only in
type annotations, so those imports live under `if TYPE_CHECKING:`.
Runtime work uses `conduit.meld()` on the object passed by `main()`.
The bootstrap imports Melder normally because it calls `md.Spellbook()`,
and imports the real application classes to register them.

In `def run_application(conduit: md.Conduit)`, `conduit` is the parameter
receiving the object from `main()`. `md.Conduit` is its type annotation.
Writing only `conduit` would still allow Python to execute the function; the
annotation supplies type information for editors and checkers.

Python 3.14 defers function annotations. This application uses the hints for
editors and type checkers and does not evaluate them during execution.

The runtime lookup is explicit: `spell="RequestHandler"` names the registered
spell. The annotation `handler: RequestHandler` describes the returned object
to your tools. It does not construct, convert, or wrap that object.

The bootstrap still imports and binds the real classes. This separates startup
from consumption while keeping the consumer's object types precise.

```{literalinclude} ../downloads/01_beginner/capstone_application.py
:language: python
:caption: capstone_application.py
```

The assertions show that configuration and pool are shared, handlers are
distinct, and their work reaches the same pool. The handler calls real methods
on its dependencies and returns an application result.

## Run the application and own shutdown

The entry point starts the graph, calls the application, and prints its results.
Its `finally` blocks guarantee that both cleanup calls are attempted if the
application raises. The pool retains a `closed` flag so this demonstration can
check that the configured disposal method ran.

```{literalinclude} ../downloads/01_beginner/40_beginner_capstone.py
:language: python
:caption: 40_beginner_capstone.py
```

From the repository root with Melder installed and Python 3.14 free-threading selected:

```bash
python UX_and_AIX_experiences/01_beginner/40_beginner_capstone.py
```

On Windows, select the free-threaded interpreter explicitly:

```powershell
py -3.14t UX_and_AIX_experiences/01_beginner/40_beginner_capstone.py
```

Expected application output after the assertions pass:

```text
orders-service: order 101 = coffee
orders-service: order 102 = tea
orders-service: order 103 = cocoa
pool closed: True
capstone complete: bootstrapped, typed, injected, used, cleaned
```

{download}`Download the Beginner collection with all four files <../downloads/beginner-examples.zip>`.
Keep the sibling modules beside the entry script when extracting or copying it.

Continue to Intermediate for more configuration and cooperation between
independently owned subsystems. The bootstrap-pattern and inventory-pattern
lessons below provide other useful ways to organize and inspect an application.
