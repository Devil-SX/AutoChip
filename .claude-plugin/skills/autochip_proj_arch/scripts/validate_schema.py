#!/usr/bin/env python3
"""
Validate JSON module files against autochip_module_schema.json

This script validates a JSON file against a schema, with support for $ref references.

Usage:
    python validate_schema.py <schema_path> <json_path>

Arguments:
    schema_path: Path to the schema JSON file
    json_path: Path to the JSON file to validate

Returns:
    0 if validation passes, 1 if validation fails
"""

import sys
import json
import argparse
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import url2pathname

try:
    from jsonschema import validate, ValidationError, RefResolver
except ImportError:
    print("Error: jsonschema package is required.")
    print("Install it with: pip install jsonschema")
    sys.exit(1)


def load_json_with_refs(file_path, base_dir=None):
    """
    Load a JSON file and resolve all $ref references recursively.

    Args:
        file_path: Path to the JSON file
        base_dir: Base directory for resolving relative paths

    Returns:
        dict: The loaded and resolved JSON data
    """
    if base_dir is None:
        base_dir = Path(file_path).parent

    with open(file_path, 'r') as f:
        data = json.load(f)

    def resolve_refs(obj, current_base):
        """Recursively resolve $ref references"""
        if isinstance(obj, dict):
            if '$ref' in obj:
                ref_path = obj['$ref']

                # Resolve relative path
                if ref_path.startswith('./') or ref_path.startswith('../'):
                    ref_file = current_base / ref_path
                    if not ref_file.exists():
                        raise FileNotFoundError(f"Referenced file not found: {ref_file}")

                    # Load referenced file
                    with open(ref_file, 'r') as rf:
                        ref_data = json.load(rf)

                    # Continue resolving refs in the referenced data
                    return resolve_refs(ref_data, ref_file.parent)
                else:
                    # For other types of refs, return as is
                    return obj

            # Recursively process dictionary values
            return {k: resolve_refs(v, current_base) for k, v in obj.items()}
        elif isinstance(obj, list):
            # Recursively process list items
            return [resolve_refs(item, current_base) for item in obj]
        else:
            return obj

    return resolve_refs(data, Path(file_path).parent)


def validate_json(schema_path, json_path, resolve_refs=True):
    """
    Validate a JSON file against a schema.

    Args:
        schema_path: Path to the schema JSON file
        json_path: Path to the JSON file to validate
        resolve_refs: Whether to resolve $ref references before validation

    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    try:
        # Load schema
        with open(schema_path, 'r') as f:
            schema = json.load(f)

        # Load JSON data
        if resolve_refs:
            data = load_json_with_refs(json_path)
        else:
            with open(json_path, 'r') as f:
                data = json.load(f)

        # Create a resolver for the schema
        schema_dir = Path(schema_path).parent
        schema_store = {schema.get("$id", ""): schema}
        resolver = RefResolver.from_schema(
            schema,
            store=schema_store
        )

        # Validate
        validate(instance=data, schema=schema, resolver=resolver)
        return True, None

    except FileNotFoundError as e:
        return False, f"File not found: {e}"
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON format in {json_path}: {e}"
    except ValidationError as e:
        error_path = ' -> '.join(str(p) for p in e.path) if e.path else 'root'
        return False, f"Validation error at '{error_path}': {e.message}"
    except Exception as e:
        return False, f"Unexpected error: {e}"


def main():
    parser = argparse.ArgumentParser(
        description='Validate JSON files against autochip_module_schema.json'
    )
    parser.add_argument(
        '--schema',
        required=True,
        help='Path to the schema JSON file'
    )
    parser.add_argument(
        '--json',
        required=True,
        dest='json_path',
        help='Path to the JSON file to validate'
    )
    parser.add_argument(
        '--no-resolve-refs',
        action='store_true',
        help='Do not resolve $ref references before validation'
    )

    args = parser.parse_args()

    schema_path = Path(args.schema)
    json_path = Path(args.json_path)

    if not schema_path.exists():
        print(f"Error: Schema file not found: {schema_path}")
        return 1

    if not json_path.exists():
        print(f"Error: JSON file not found: {json_path}")
        return 1

    print(f"Validating: {json_path}")
    print(f"Using schema: {schema_path}")
    print()

    is_valid, error_msg = validate_json(
        schema_path,
        json_path,
        resolve_refs=not args.no_resolve_refs
    )

    if is_valid:
        print("✓ Validation PASSED")
        return 0
    else:
        print("✗ Validation FAILED")
        print(f"  Error: {error_msg}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
