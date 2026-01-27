# AutoChip Module Schema Scripts

This directory contains Python scripts for working with autochip module JSON files.

## Prerequisites

Install required Python package:
```bash
pip install jsonschema
```

## Scripts

All scripts use **named arguments** for required parameters.

### 1. validate_schema.py

Validate JSON files against autochip_module_schema.json with support for `$ref` references.

```bash
python scripts/validate_schema.py --schema <schema_path> --json <json_path> [--no-resolve-refs]
```

| Argument | Type | Description |
|----------|------|-------------|
| `--schema` | string | Path to the schema JSON file (required) |
| `--json` | string | Path to the JSON file to validate (required) |
| `--no-resolve-refs` | flag | Skip resolving `$ref` references before validation |

**Example:**
```bash
python validate_schema.py --schema autochip_module_schema.json --json cpu.json
```

**Exit codes:**
- `0`: Validation passed
- `1`: Validation failed

---

### 2. extract_modules.py

Extract all modules from a JSON file, including those referenced via `$ref`.

```bash
python scripts/extract_modules.py --schema <schema_path> --json <json_path> [--format FORMAT] [-o OUTPUT]
```

| Argument | Type | Description |
|----------|------|-------------|
| `--schema` | string | Path to the schema JSON file (required) |
| `--json` | string | Path to the JSON file to extract from (required) |
| `--format` | string | Output format: `table`, `json`, `tree` (default: table) |
| `-o, --output` | string | Output file path (default: stdout) |

**Examples:**
```bash
# Table format (default)
python extract_modules.py --schema autochip_module_schema.json --json cpu.json

# Tree format
python extract_modules.py --schema autochip_module_schema.json --json cpu.json --format tree

# JSON format to file
python extract_modules.py --schema autochip_module_schema.json --json cpu.json --format json -o modules.json
```

---

### 3. extract_testcases.py

Extract all test cases from a JSON file, including those from modules referenced via `$ref`.

```bash
python scripts/extract_testcases.py --schema <schema_path> --json <json_path> [--format FORMAT] [-o OUTPUT] [--filter-module MODULE]
```

| Argument | Type | Description |
|----------|------|-------------|
| `--schema` | string | Path to the schema JSON file (required) |
| `--json` | string | Path to the JSON file to extract from (required) |
| `--format` | string | Output format: `table`, `json`, `summary` (default: table) |
| `-o, --output` | string | Output file path (default: stdout) |
| `--filter-module` | string | Only show test cases for a specific module |

**Examples:**
```bash
# Table format (default)
python extract_testcases.py --schema autochip_module_schema.json --json cpu.json

# Summary format
python extract_testcases.py --schema autochip_module_schema.json --json cpu.json --format summary

# JSON format
python extract_testcases.py --schema autochip_module_schema.json --json cpu.json --format json

# Filter by specific module
python extract_testcases.py --schema autochip_module_schema.json --json cpu.json --filter-module alu

# Save to file
python extract_testcases.py --schema autochip_module_schema.json --json cpu.json -o testcases.json
```

---

## $ref Reference Support

All scripts support resolving `$ref` references to external JSON files. When a module references another module via:

```json
{
  "submodules": [
    { "$ref": "./alu.json" }
  ]
}
```

The scripts will:
1. Load the referenced file (`./alu.json`)
2. Resolve any nested references recursively
3. Include the referenced module data in the output

---

## Example Workflow

```bash
# 1. Validate a module file
python scripts/validate_schema.py --schema autochip_module_schema.json --json cpu.json

# 2. Extract all modules in tree format
python scripts/extract_modules.py --schema autochip_module_schema.json --json cpu.json --format tree

# 3. Extract all test cases in summary format
python scripts/extract_testcases.py --schema autochip_module_schema.json --json cpu.json --format summary
```
