# JSON Schema generation

## `test.sh`

**Per-theme-type schema validation** - No monolithic schema support.

Key features:

- **Schema validation**: Tests all per-theme-type schemas (e.g., `overture-schema-base-land_cover.json`)
- **Examples validation**: Validates all files in reference/examples/ (should pass)
- **Counterexamples validation**: Validates all files in reference/counterexamples/ (should fail)
- **Content-based theme/type extraction**: Uses `yq` to read `properties.theme` and `properties.type` from files
- **Pattern matching**: Supports filtering tests by regex patterns
- **Mode selection**: Can run specific validation modes with -m flag
- **Expected error checking**: Uses yq to check for expected errors in counterexamples

Usage examples:

```bash
./test.sh                    # Run all tests
./test.sh -m schema          # Validate all per-theme-type schemas
./test.sh -m examples        # Run only example validation
./test.sh -m counterexamples # Run only counterexample validation
./test.sh "transportation.*" # Run tests matching pattern
./test.sh -v                 # Verbose mode shows theme:type detection
```

## Schema Generation

The script automatically generates per-theme-type schemas as needed:

```bash
# Generate specific schema
uv run python -m packages.overture-schema.src.overture.schema --theme base --type land_cover

# List all available combinations
uv run python -m packages.overture-schema.src.overture.schema --list-types

# Generate all schemas to a directory
uv run python -m packages.overture-schema.src.overture.schema --output-dir schemas/
```

**Important**: Monolithic schema generation is no longer supported. Each example/counterexample is validated against its specific theme-type schema.

## Prerequisites

- `jv` (JSON validator) available in `~/go/bin`
- `yq` for theme/type extraction from YAML/JSON files
- `/opt/homebrew/bin/bash` (newer bash features required)

This was adapted from overture/schema's `test.sh` and is intended to help
refine how Pydantic generates JSON Schema for Overture.
