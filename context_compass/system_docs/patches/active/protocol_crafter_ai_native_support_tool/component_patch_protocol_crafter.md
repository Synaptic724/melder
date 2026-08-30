# Component Patch: ProtocolCrafter

## Purpose
Provide a small utility object for protocol generation and interface-file
maintenance.

## Public Surface
- craft protocol code from class/object input
- append generated protocol code into an interface file
- remove an existing protocol block from an interface file

## Core Rules
- prefix protocol name with `I`
- mirror class and method docstrings when present
- generate fallback docstrings when missing
- mirror attributes and methods into protocol shape
- methods always use `...` bodies
- optional inheritance walk through the target MRO
