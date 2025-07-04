# JSON Schema generation

## `test.sh`

Key features:

- Schema validation: Tests the generated overture-schema.json file itself
- Examples validation: Validates all files in reference/examples/ (should pass)
- Counterexamples validation: Validates all files in reference/counterexamples/ (should fail)
- Pattern matching: Supports filtering tests by regex patterns
- Mode selection: Can run specific validation modes with -m flag
- Expected error checking: Uses yq to check for expected errors in counterexamples

Usage examples:
./test.sh                    # Run all tests
./test.sh -m examples        # Run only example validation
./test.sh -m counterexamples # Run only counterexample validation
./test.sh "transportation.*" # Run tests matching pattern

The script uses jv (JSON validator) to validate against the Pydantic-generated JSON Schema at
./overture-schema.json.

This was adapted from overture/schema's `test.sh` and is intended to help
refine how Pydantic generates JSON Schema for Overture.
