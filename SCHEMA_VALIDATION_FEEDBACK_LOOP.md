# Schema Validation Feedback Loop

This document describes the iterative process for improving our Pydantic schema implementation to match the intended validation behavior of the reference JSON Schema.

## Overview

The feedback loop helps identify and fix discrepancies between our Pydantic-generated JSON Schema and the expected validation behavior by testing against known examples and counterexamples.

**Important distinction:** This process focuses on the **generated JSON Schema output** (`overture-schema.json`), not direct Pydantic model validation. Field validation and model-level configuration issues are typically caught earlier when testing Pydantic models directly against examples. This feedback loop specifically targets cases where the Pydantic models work correctly but their JSON Schema generation doesn't capture all the intended validation rules.

## Prerequisites

- Ensure `jv` (JSON validator) is available in `~/go/bin`
- Use `/opt/homebrew/bin/bash` for running test scripts (newer bash features required)
- Have `yq` installed for enhanced counterexample testing

## Feedback Loop Steps

### 1. Generate Schema Snapshot

Generate the current JSON Schema from your Pydantic models:

```bash
uv run python -m packages.overture-schema.src.overture.schema > overture-schema.json
```

This captures the current state of all Pydantic models' JSON Schema output in a single file.

### 2. Run Validation Tests

Execute the test suite against examples and counterexamples:

```bash
PATH="$PATH:$HOME/go/bin" /opt/homebrew/bin/bash ./test.sh
```

**Test modes available:**

- `./test.sh` - Run all tests (schema, examples, counterexamples)
- `./test.sh -m examples` - Test only positive examples (should pass)
- `./test.sh -m counterexamples` - Test only negative examples (should fail)
- `./test.sh "pattern"` - Test files matching regex pattern

### 3. Inspect Failures

**Example failures (should pass but failed):**

- Indicates the Pydantic schema is too strict
- Look for missing optional fields, overly restrictive validation, or type mismatches
- Check the detailed error output for specific validation failures

**Counterexample failures (should fail but passed):**

- Indicates the Pydantic schema is too permissive
- Look for missing required fields, missing validation constraints, or missing type restrictions
- These are often the most critical to fix as they represent security/data quality issues

**Detailed error inspection:**

```bash
# Get detailed validation output for specific failing files
PATH="$PATH:$HOME/go/bin" /opt/homebrew/bin/bash -c "jv --output detailed overture-schema.json reference/counterexamples/path/to/failing-file.yaml"
```

### 4. Update Pydantic Models

Focus on customizing JSON Schema generation using Pydantic's schema customization features:

**Common fixes:**

a) **Custom field validation:**

```python
from pydantic import Field, field_validator
from typing_extensions import Annotated

class MyModel(BaseModel):
    field: Annotated[str, Field(min_length=1)]  # Prevent empty strings
    
    @field_validator('field')
    def validate_field(cls, v):
        # Custom validation logic
        return v
```

b) **JSON Schema customization:**

```python
from pydantic import BaseModel
from pydantic.json_schema import GenerateJsonSchema, JsonSchemaValue
from typing import Any

class MyModel(BaseModel):
    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: Any, handler: Any
    ) -> JsonSchemaValue:
        json_schema = handler(core_schema)
        # Customize the generated JSON Schema
        json_schema['additionalProperties'] = False  # Strict property checking
        return json_schema
```

c) **Model-level configuration:**

```python
from pydantic import BaseModel, ConfigDict

class MyModel(BaseModel):
    model_config = ConfigDict(
        extra='forbid',  # Reject extra fields
        str_strip_whitespace=True,  # Auto-strip strings
        validate_assignment=True,  # Validate on assignment
    )
```

**Target specific issues:**

- **Too permissive**: Add field constraints, required fields, enum restrictions
- **Too strict**: Make fields optional, allow additional properties, relax type constraints
- **Missing validation**: Add custom validators, field constraints, or model validators

### 5. Repeat the Loop

After making changes:

1. Regenerate schema: `uv run python -m packages.overture-schema.src.overture.schema > overture-schema.json`
2. Re-run tests: `PATH="$PATH:$HOME/go/bin" /opt/homebrew/bin/bash ./test.sh`
3. Compare results to previous run
4. Continue until all tests pass

## Tracking Progress

**Monitor test results:**

```bash
# Count passing/failing tests
PATH="$PATH:$HOME/go/bin" /opt/homebrew/bin/bash ./test.sh 2>&1 | grep -c "OK"
PATH="$PATH:$HOME/go/bin" /opt/homebrew/bin/bash ./test.sh 2>&1 | grep -c "FAILED"
```

**Focus areas by priority:**

1. **Counterexamples passing** (highest priority - security/data quality)
2. **Examples failing** (medium priority - usability)
3. **Schema validation** (basic prerequisite)

## Debugging Tips

**Understanding validation failures:**

- Use `jv --output detailed` for comprehensive error messages
- Check the specific line/property causing validation failures
- Compare against the source of truth: hand-written JSON Schema in
  `../schema/schema/` (YAML files)
- Note: Our generated JSON Schema doesn't need to match exactly, but should
  validate the same data correctly

**Common Pydantic schema issues:**

- Missing `Field(...)` constraints
- Incorrect use of `Optional` vs required fields
- Union types not properly constrained
- Missing custom validators for complex business rules
- Incorrect `additionalProperties` handling

**Testing specific patterns:**

```bash
# Test only transportation-related files
./test.sh "transportation"

# Test only a specific counterexample category
./test.sh -m counterexamples "addresses"
```

## Success Criteria

The feedback loop is complete when:

- ✅ Schema validation passes (`overture-schema.json` is valid)
- ✅ All examples pass validation (positive test cases)
- ✅ All counterexamples fail validation (negative test cases)
- ✅ Generated JSON Schema semantically matches reference behavior

This iterative process ensures the Pydantic implementation accurately reflects the intended validation rules of the Overture Maps schema.
