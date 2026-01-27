#!/usr/bin/env python3
"""
Extract all test cases from autochip module JSON files

This script extracts all test case definitions from a JSON file,
including test cases from modules referenced via $ref.

Usage:
    python extract_testcases.py <schema_path> <json_path>

Arguments:
    schema_path: Path to the schema JSON file (for validation)
    json_path: Path to the JSON file to extract test cases from

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


def extract_testcases(data: dict, module_name: str = "", visited: Set[str] = None) -> List[Dict]:
    """
    Recursively extract all test cases from the data structure.

    Args:
        data: The JSON data to extract test cases from
        module_name: Current module name for context
        visited: Set of visited modules to avoid duplicates

    Returns:
        list: List of test case dictionaries
    """
    if visited is None:
        visited = set()

    testcases = []

    # Check if current data is a module
    if isinstance(data, dict) and 'name' in data:
        current_module = data['name']

        # Avoid processing same module multiple times
        if current_module in visited:
            return testcases
        visited.add(current_module)

        # Extract test cases if present
        test_config = data.get('test')
        if test_config and isinstance(test_config, dict):
            test_case_list = test_config.get('test_case', [])
            if test_case_list and isinstance(test_case_list, list):
                for idx, tc in enumerate(test_case_list):
                    if isinstance(tc, dict):
                        testcase_info = {
                            'module': current_module,
                            'module_path': module_name,
                            'test_name': tc.get('name', f'test_{idx}'),
                            'run_cmd': tc.get('run_cmd', ''),
                            'output_log_path': tc.get('output_log_path', []),
                            'output_wave_path': tc.get('output_wave_path', None),
                            'testbench_path': test_config.get('testbench_path', ''),
                            'golden_model_path': test_config.get('golden_model_path', '')
                        }
                        testcases.append(testcase_info)

        # Recursively extract from submodules
        submodules = data.get('submodules')
        if submodules:
            if isinstance(submodules, list):
                for submodule in submodules:
                    if isinstance(submodule, dict):
                        full_module_path = f"{module_name}/{current_module}" if module_name else current_module
                        testcases.extend(
                            extract_testcases(submodule, full_module_path, visited)
                        )
            elif isinstance(submodules, dict):
                full_module_path = f"{module_name}/{current_module}" if module_name else current_module
                testcases.extend(
                    extract_testcases(submodules, full_module_path, visited)
                )

    return testcases


def main():
    parser = argparse.ArgumentParser(
        description='Extract all test cases from autochip module JSON files'
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
        help='Path to the JSON file to extract test cases from'
    )
    parser.add_argument(
        '--format',
        choices=['table', 'json', 'summary'],
        default='table',
        help='Output format (default: table)'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file path (default: stdout)'
    )
    parser.add_argument(
        '--filter-module',
        help='Only show test cases for a specific module'
    )

    args = parser.parse_args()

    json_path = Path(args.json_path)

    if not json_path.exists():
        print(f"Error: JSON file not found: {json_path}", file=sys.stderr)
        return 1

    try:
        # Load and resolve refs
        data = load_json_with_refs(json_path)

        # Extract test cases
        testcases = extract_testcases(data)

        if not testcases:
            print("No test cases found in the JSON file.", file=sys.stderr)
            return 1

        # Filter by module if requested
        if args.filter_module:
            testcases = [tc for tc in testcases if tc['module'] == args.filter_module]
            if not testcases:
                print(f"No test cases found for module: {args.filter_module}", file=sys.stderr)
                return 1

        # Output results
        output = sys.stdout
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output = open(output_path, 'w')

        try:
            if args.format == 'json':
                json.dump(testcases, output, indent=2)
                output.write('\n')
            elif args.format == 'summary':
                # Group by module
                by_module = {}
                for tc in testcases:
                    module = tc['module']
                    if module not in by_module:
                        by_module[module] = []
                    by_module[module].append(tc)

                output.write("Test Case Summary\n")
                output.write("=" * 60 + '\n\n')
                for module, cases in sorted(by_module.items()):
                    output.write(f"Module: {module}\n")
                    output.write(f"  Total test cases: {len(cases)}\n")
                    for tc in cases:
                        output.write(f"    - {tc['test_name']}\n")
                    output.write('\n')
                output.write(f"\nTotal modules with tests: {len(by_module)}\n")
                output.write(f"Total test cases: {len(testcases)}\n")
            else:  # table format
                # Table header
                output.write(f"{'Module':<20} | {'Test Name':<25} | {'Run Command':<40} | {'Wave':<6}\n")
                output.write('-' * 100 + '\n')
                for tc in testcases:
                    wave_status = '✓' if tc.get('output_wave_path') else '-'
                    cmd = tc['run_cmd'][:37] + '...' if len(tc['run_cmd']) > 40 else tc['run_cmd']
                    output.write(
                        f"{tc['module']:<20} | "
                        f"{tc['test_name']:<25} | "
                        f"{cmd:<40} | "
                        f"{wave_status:<6}\n"
                    )

            output.write(f"\nTotal: {len(testcases)} test case(s)\n")

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
