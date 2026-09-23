# What you can bind

Registration is ordinary Python code. The saved lessons demonstrate three
useful inputs: a class Melder can construct, a function that supplies a value,
and an instance you already constructed.

Registration takes the Python object: `book.bind(spell=Greeter, existence="unique")`.
Resolution uses its registered name: `conduit.meld("Greeter")`. Function spells use
their function names, such as `conduit.meld("make_settings")`. A prebuilt instance
uses its type's name, such as `conduit.meld("AlreadyBuilt")`; the local variable
holding that instance is not its registered name.

## Pick the form that expresses your ownership

Use the class examples when you want to study construction and instance
lifetimes. Use the function and prebuilt-instance examples when a value comes
from application setup you already control. Read their assertions before
assuming that all registration forms have interchangeable lifetime behavior.

## Bind an existing object under a Protocol

An existing object uses `existence="unique"`. When you supply a Protocol as
`spellframe`, Melder checks the actual object during bind: public members defined
directly on that Protocol must exist, and callable members must be callable.
An incompatible object raises `TypeError` before registration. Compatible objects
can be injected into consumers, preserving the original reference.

This is a limited member check, not full static type checking. It does not check
inherited Protocol declarations, annotation-only data fields or method signatures.
Members supplied by the instance itself can satisfy the check. Factory bindings
retain their separate callable contract.

## Register a group of services

The collection examples show both a normal loop over registrations and a
prebuilt registry bound as one value. These answer different questions:
registering several services exposes several graph entries; supplying a registry
exposes the collection your application already owns.

The linked lessons contain the full classes, setup, and checks. Work through
one form at a time, then use the capstone to put them together.
