# Install and run Melder

Start with Python 3.14 or newer. The saved example curriculum uses the
free-threaded build of Python 3.14.

## Check your interpreter

```bash
python -VV
```

A free-threaded interpreter includes `free-threading build` in that output.
The official Python installation guide explains how to select that build:
[Python support for free threading](https://docs.python.org/3.14/howto/free-threading-python.html).

On Windows, an installed free-threaded 3.14 interpreter can be selected explicitly:

```powershell
py -3.14t -VV
```

## Install the package

Use the same interpreter for installation and execution:

```bash
python -m pip install melder
```

```powershell
py -3.14t -m pip install melder
```

Melder has no runtime package dependencies. Application code imports the public
namespace as `import melder as md`.

## Get the runnable examples

The Examples section provides individual source views and complete level
downloads. A collection download preserves its directory structure and local
helpers. From the extracted collection root, run the command printed on the
lesson page.

If working from the repository itself, install the current checkout first:

```bash
python -m pip install -e .
python UX_and_AIX_experiences/01_beginner/01_hello_meld.py
```

Keep the package version and the documentation version aligned when comparing
behavior. The first lesson gives you a small complete script with assertions.
