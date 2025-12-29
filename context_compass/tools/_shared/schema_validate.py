"""Minimal JSON schema validation helpers for context_compass."""

from pathlib import Path
from typing import Any, Mapping

from context_compass.tools._shared.json_io import load_json


def load_schema(path: Path) -> Mapping[str, object]:
    """
    Load a JSON schema from disk.

    Args:
        path (Path): Path to schema JSON.

    Returns:
        Mapping[str, object]: Parsed schema data.
    """
    data = load_json(path)
    if not isinstance(data, dict):
        raise ValueError(f"Schema at {path} is not an object")
    return data


def validate_schema(data: Any, schema: Mapping[str, object], path: str = "$") -> list[str]:
    """
    Validate data against a minimal JSON schema subset.

    Supported keywords: type, required, properties, items, enum, const, additionalProperties.

    Args:
        data (Any): JSON data to validate.
        schema (Mapping[str, object]): Schema definition.
        path (str): JSON pointer for error messages.

    Returns:
        list[str]: List of validation error messages.
    """
    errors: list[str] = []
    schema_type = schema.get("type")
    if schema_type is not None:
        if not _matches_type(data, schema_type):
            errors.append(f"{path}: expected type {schema_type}")
            return errors

    if "const" in schema and data != schema["const"]:
        errors.append(f"{path}: value must equal {schema['const']}")

    if "enum" in schema and data not in schema["enum"]:
        errors.append(f"{path}: value not in enum")

    if isinstance(data, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in data:
                errors.append(f"{path}: missing required key '{key}'")
        properties = schema.get("properties", {})
        if isinstance(properties, dict):
            for key, value in data.items():
                if key in properties:
                    prop_schema = properties[key]
                    if isinstance(prop_schema, dict):
                        errors.extend(validate_schema(value, prop_schema, f"{path}.{key}"))
                else:
                    if schema.get("additionalProperties") is False:
                        errors.append(f"{path}: unexpected key '{key}'")
        return errors

    if isinstance(data, list):
        items_schema = schema.get("items")
        if isinstance(items_schema, dict):
            for index, item in enumerate(data):
                errors.extend(validate_schema(item, items_schema, f"{path}[{index}]"))
        return errors

    return errors


def _matches_type(data: Any, schema_type: object) -> bool:
    if isinstance(schema_type, list):
        return any(_matches_type(data, t) for t in schema_type)
    if schema_type == "object":
        return isinstance(data, dict)
    if schema_type == "array":
        return isinstance(data, list)
    if schema_type == "string":
        return isinstance(data, str)
    if schema_type == "integer":
        return isinstance(data, int) and not isinstance(data, bool)
    if schema_type == "number":
        return isinstance(data, (int, float)) and not isinstance(data, bool)
    if schema_type == "boolean":
        return isinstance(data, bool)
    if schema_type == "null":
        return data is None
    return True
