"""FORWARDREF-first vs VALUE-first signature text for a dataclass whose field types all resolve.

Usage: python -X gil=0 probe_dataclass_forwardref.py <order: forwardref_first|value_first>
"""
import inspect
import sys
from annotationlib import Format
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Row:
    price: Decimal
    qty: int = 0


if sys.argv[1] == "value_first":
    print("VALUE     :", inspect.signature(Row))
print("FORWARDREF:", inspect.signature(Row, annotation_format=Format.FORWARDREF))
print("VALUE     :", inspect.signature(Row))
print("FORWARDREF:", inspect.signature(Row, annotation_format=Format.FORWARDREF))
