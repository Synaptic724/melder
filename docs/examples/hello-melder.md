# Hello Melder

**🟢 Beginner · First contact · Binding and resolution**

Build a graph containing one plain Python class. The example uses the public
Melder namespace and demonstrates that `unique` returns the same instance on
the second resolution.

## Run it

From the repository root, with Melder installed:

```bash
python UX_and_AIX_experiences/01_beginner/01_hello_meld.py
```

On Windows, select the free-threaded interpreter explicitly when needed:

```powershell
py -3.14t UX_and_AIX_experiences/01_beginner/01_hello_meld.py
```

## The saved example

```{literalinclude} ../downloads/01_hello_meld.py
:language: python
:linenos:
```

{download}`Download the script <../downloads/01_hello_meld.py>`

## What to observe

The script calls `bind`, then `conjure`, then `meld`. Its assertions check that
the result is a `Greeter`, that the runtime is a `Conduit`, and that resolving
the unique spell again returns the identical object.

The printed greeting comes from the ordinary Python method on the resolved
instance. The assertion outcomes are checked when you run the script; this
page does not fabricate a captured run.

[Continue with Beginner](../beginner/index.md) · [All examples](index.md)
