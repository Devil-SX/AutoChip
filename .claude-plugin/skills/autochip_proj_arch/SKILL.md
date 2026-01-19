---
name: autochip_proj_arch
description: AutoChip project configuration structure and utilities for managing IC module metadata, including schema validation and extraction tools.
---

This SKILL describes the AutoChip project configuration. All configurations are contained in a directory named `.autochip` with the following structure:

```
.autochip/
├── env.yaml              # Environment configuration file
└── modules/
    ├── <module_name>.json
    └── <module_name>.json
```

## Environment Configuration

The `env.yaml` file describing the necessary env.

## Module Definitions

Module JSON files are the core metadata for project interaction. Each module must satisfy the [Schema](autochip_module_schema.json) definition.

### Module Structure

```json
{
  "name": "module_name",
  "filepath": "path/to/rtl.v",
  "docpath": "path/to/doc.md",
  "submodules": [
    { "$ref": "./other_module.json" }
  ],
  "test": {
    "testbench_path": "path/to/testbench.sv",
    "golden_model_path": "path/to/model.py",
    "test_case": [
      {
        "name": "test_basic",
        "run_cmd": "make test",
        "output_log_path": ["logs/test.log"]
      }
    ]
  }
}
```

---

## Scripts

Located in `scripts/` directory. All scripts use named arguments.

### validate_schema.py

Validate JSON files against the autochip module schema with `$ref` support.

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
python scripts/validate_schema.py --schema autochip_module_schema.json --json cpu.json
```

---

### extract_modules.py

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

**Example:**
```bash
# Tree format
python scripts/extract_modules.py --schema autochip_module_schema.json --json cpu.json --format tree

# JSON format to file
python scripts/extract_modules.py --schema autochip_module_schema.json --json cpu.json --format json -o modules.json
```

---

### extract_testcases.py

Extract all test cases from a JSON file, including those from referenced modules.

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

**Example:**
```bash
# Summary format
python scripts/extract_testcases.py --schema autochip_module_schema.json --json cpu.json --format summary

# Filter by module
python scripts/extract_testcases.py --schema autochip_module_schema.json --json cpu.json --filter-module alu
```

---

## $ref Reference Support

All scripts support resolving `$ref` references to external JSON files. When a module references another via:

```json
{
  "submodules": [
    { "$ref": "./alu.json" }
  ]
}
```

The scripts will:
1. Load the referenced file (`./alu.json`)
2. Resolve nested references recursively
3. Include the referenced module data in the output
