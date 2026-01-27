#!/usr/bin/env python3
"""
Extract all modules from autochip module JSON files

This script extracts all module definitions from a JSON file,
including modules referenced via $ref.

Usage:
    python extract_modules.py <schema_path> <json_path>

Arguments:
    schema_path: Path to the schema JSON file (for validation)
    json_path: Path to the JSON file to extract modules from

Returns:
    0 if successful, 1 if an error occurs
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Set


def load_json_with_refs(file_path: Path, base_dir: Path = None) -> dict:
    """
    Load a JSON file and resolve all $ref references recursively.

    Args:
        file_path: Path to the JSON file
        base_dir: Base directory for resolving relative paths

    Returns:
        dict: The loaded and resolved JSON data
    """
    if base_dir is None:
        base_dir = file_path.parent

    with open(file_path, 'r') as f:
        data = json.load(f)

    def resolve_refs(obj, current_base: Path):
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

    return resolve_refs(data, file_path.parent)


def extract_modules(data: dict, parent_name: str = "", visited: Set[str] = None) -> List[Dict]:
    """
    Recursively extract all modules from the data structure.

    Args:
        data: The JSON data to extract modules from
        parent_name: Parent module name for tracking hierarchy
        visited: Set of visited module names to avoid duplicates

    Returns:
        list: List of module dictionaries with hierarchy info
    """
    if visited is None:
        visited = set()

    modules = []

    # Check if current data is a module (has required fields)
    if isinstance(data, dict) and all(key in data for key in ['name', 'filepath', 'docpath']):
        module_name = data['name']

        # Avoid duplicates
        full_name = f"{parent_name}/{module_name}" if parent_name else module_name
        if full_name not in visited:
            visited.add(full_name)

            module_info = {
                'name': module_name,
                'filepath': data.get('filepath', ''),
                'docpath': data.get('docpath', ''),
                'parent': parent_name if parent_name else None,
                'full_path': full_name,
                'has_test': 'test' in data,
                'has_submodules': bool(data.get('submodules'))
            }

            modules.append(module_info)

            # Recursively extract submodules
            submodules = data.get('submodules')
            if submodules:
                if isinstance(submodules, list):
                    for submodule in submodules:
                        if isinstance(submodule, dict):
                            modules.extend(
                                extract_modules(submodule, full_name, visited)
                            )
                elif isinstance(submodules, dict):
                    modules.extend(
                        extract_modules(submodules, full_name, visited)
                    )

    return modules


def main():
    parser = argparse.ArgumentParser(
        description='Extract all modules from autochip module JSON files'
    )
    parser.add_argument(
        '--schema',
        required=True,
        dest='schema_path',
        help='Path to the schema JSON file'
    )
    parser.add_argument(
        '--json',
        required=True,
        dest='json_path',
        help='Path to the JSON file to extract modules from'
    )
    parser.add_argument(
        '--format',
        choices=['table', 'json', 'tree'],
        default='table',
        help='Output format (default: table)'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file path (default: stdout)'
    )

    args = parser.parse_args()

    json_path = Path(args.json_path)

    if not json_path.exists():
        print(f"Error: JSON file not found: {json_path}", file=sys.stderr)
        return 1

    try:
        # Load and resolve refs
        data = load_json_with_refs(json_path)

        # Extract modules
        modules = extract_modules(data)

        if not modules:
            print("No modules found in the JSON file.", file=sys.stderr)
            return 1

        # Output results
        output = sys.stdout
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output = open(output_path, 'w')

        try:
            if args.format == 'json':
                json.dump(modules, output, indent=2)
                output.write('\n')
            elif args.format == 'tree':
                # Build tree structure
                def build_tree(mods):
                    tree = {}
                    for mod in mods:
                        parts = mod['full_path'].split('/')
                        current = tree
                        for i, part in enumerate(parts):
                            if part not in current:
                                current[part] = {} if i < len(parts) - 1 else None
                            if i < len(parts) - 1:
                                current = current[part]
                    return tree

                def print_tree(tree, indent=0, prefix=''):
                    for i, (name, children) in enumerate(tree.items()):
                        is_last = i == len(tree) - 1
                        connector = '└── ' if is_last else '├── '
                        output.write('  ' * indent + prefix + connector + name + '\n')

                        if children is not None:
                            new_prefix = '    ' if is_last else '│   '
                            print_tree(children, indent + 1, prefix + new_prefix)

                tree = build_tree(modules)
                print_tree(tree)
            else:  # table format
                # Table header
                output.write(f"{'Module Path':<40} | {'File':<30} | {'Doc':<30} | {'Test':<6}\n")
                output.write('-' * 125 + '\n')
                for mod in modules:
                    test_status = '✓' if mod['has_test'] else '-'
                    output.write(
                        f"{mod['full_path']:<40} | "
                        f"{mod['filepath']:<30} | "
                        f"{mod['docpath']:<30} | "
                        f"{test_status:<6}\n"
                    )

            output.write(f"\nTotal: {len(modules)} module(s)\n")

        finally:
            if args.output:
                output.close()

        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in {json_path}: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
