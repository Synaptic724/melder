# What you can bind

Registration is ordinary Python code. The saved lessons demonstrate three
useful inputs: a class Melder can construct, a function that supplies a value,
and an instance you already constructed.

## Pick the form that expresses your ownership

Use the class examples when you want to study construction and instance
lifetimes. Use the function and prebuilt-instance examples when a value comes
from application setup you already control. Read their assertions before
assuming that all registration forms have interchangeable lifetime behavior.

## Register a group of services

The collection examples show both a normal loop over registrations and a
prebuilt registry bound as one value. These answer different questions:
registering several services exposes several graph entries; supplying a registry
exposes the collection your application already owns.

The linked lessons contain the full classes, setup, and checks. Work through
one form at a time, then use the capstone to put them together.
