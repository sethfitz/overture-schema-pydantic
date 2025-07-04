# Schema Validation Feedback Loop

This document describes the iterative process for improving our Pydantic schema implementation to match the intended validation behavior of the reference JSON Schema.

## Overview

The feedback loop helps identify and fix discrepancies between our Pydantic-generated JSON Schema and the expected validation behavior by testing against known examples and counterexamples.

**Key insight:** The major breakthrough was discovering that the monolithic schema approach doesn't work because it lacks conditional routing logic (`if/then/else` based on `theme` and `type`). The solution is **per-theme-type schema generation** that matches how examples are organized.

## Prerequisites

- Ensure `jv` (JSON validator) is available in `~/go/bin`
- Use `/opt/homebrew/bin/bash` for running test scripts (newer bash features required)
- Have `yq` installed for enhanced counterexample testing

## Feedback Loop Steps

### 0. Start Clean - Pydantic Model Validation

**CRITICAL:** Always verify Pydantic models work correctly before testing JSON Schema generation.

```bash
# Run constraint validation tests
uv run pytest packages/overture-schema-validation/test_constraints.py -v

# Run baseline tests (may have cache issues - clear if needed)
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
uv run pytest packages/overture-schema-address-type/tests/ -v
```

**Test your specific models directly:**

```bash
uv run python -c "
import sys
sys.path.append('packages/overture-schema-address-type/src')
from overture.schema.addresses.address.models import AddressFeature

# Test the failing counterexample data
test_data = {
    'id': 'test:1', 'type': 'Feature',
    'geometry': {'type': 'Point', 'coordinates': [-71, 42]},
    'properties': {
        'theme': 'addresses', 'type': 'address', 'version': 0,
        'country': 'US', 'address_levels': []  # Should fail
    }
}

try:
    AddressFeature(**test_data)
    print('❌ PYDANTIC VALIDATION PASSED - This indicates a model issue')
except Exception as e:
    print('✅ PYDANTIC VALIDATION FAILED (correctly):', str(e))
"
```

**If Pydantic validation fails to catch issues, fix the models first using constraint-based validation:**

```python
from typing import Annotated, List
from overture.schema.validation import MinItemsConstraint, WhitespaceConstraint

# Use constraints instead of basic Field parameters
address_levels: Annotated[List[AddressLevel], MinItemsConstraint(1), MaxItemsConstraint(5)]
street: Optional[Annotated[str, WhitespaceConstraint()]]
```

### 1. Generate Per-Theme-Type Schemas

**NEW APPROACH:** Generate individual schema files for each theme-type combination instead of one monolithic schema.

```bash
# List all available theme-type combinations
uv run python -m packages.overture-schema.src.overture.schema --list-types

# Generate specific schema for testing
uv run python -m packages.overture-schema.src.overture.schema --theme addresses --type address > overture-schema-addresses-address.json

# Or generate all schemas at once
uv run python -m packages.overture-schema.src.overture.schema --output-dir schemas/
```

**Why this works:** Each example/counterexample has a known `theme` and `type`, so we can validate against the specific schema for that combination, avoiding the need for complex conditional routing.

### 2. Test Against Specific Schemas

**OLD (didn't work):**

```bash
# This approach failed because of missing routing logic
PATH="$PATH:$HOME/go/bin" jv overture-schema.json reference/counterexamples/addresses/bad-address-empty-levels.yaml
```

**NEW (works correctly):**

```bash
# Test against specific theme-type schema
PATH="$PATH:$HOME/go/bin" jv --output detailed overture-schema-addresses-address.json reference/counterexamples/addresses/bad-address-empty-levels.yaml
```

### 3. Validate Results

**Expected behavior for counterexamples:**

```bash
# Should FAIL with specific error messages
PATH="$PATH:$HOME/go/bin" jv overture-schema-addresses-address.json reference/counterexamples/addresses/bad-address-empty-levels.yaml
# Expected: "minItems: got 0, want 1"

PATH="$PATH:$HOME/go/bin" jv overture-schema-addresses-address.json reference/counterexamples/addresses/bad-address-too-many-levels.yaml  
# Expected: "maxItems: got 6, want 5"
```

**Expected behavior for examples:**

```bash
# Should PASS without errors
PATH="$PATH:$HOME/go/bin" jv overture-schema-addresses-address.json reference/examples/addresses/address.yaml
```

### 4. Diagnose Schema Generation Issues

**Common problems discovered:**

a) **Constraint not generating JSON Schema properly:**

```bash
# Check if constraint appears in generated schema
jq '.["$defs"].AddressProperties.properties.street' overture-schema-addresses-address.json
```

If missing expected patterns/constraints, the issue is in constraint implementation:

- `MinItemsConstraint()` → should generate `"minItems": N`
- `WhitespaceConstraint()` → should generate `"pattern": "^(\\S.*)?\S$"`
- `CountryCodeConstraint()` → should generate `"pattern": "^[A-Z]{2}$"`

b) **Missing required fields:**

```bash
# Check required array
jq '.["$defs"].AddressProperties.required' overture-schema-addresses-address.json
```

c) **Type routing issues:**

```bash  
# Check theme/type constraints
jq '.["$defs"].AddressProperties.properties.theme' overture-schema-addresses-address.json
# Should show: {"const": "addresses", ...}
```

### 5. Fix Issues Systematically

**Priority order:**

1. **High Priority - Missing JSON Schema generation in constraints**
   - Fix constraint classes to properly implement `__get_json_schema__()` methods
   - Test: Generate schema and verify constraint appears

2. **Medium Priority - Field-level validation issues**  
   - Add missing constraints to model fields
   - Use `Annotated[Type, Constraint()]` syntax

3. **Low Priority - Model structure issues**
   - Adjust required fields, optional handling

**Example fixes:**

```python
# Fix constraint that doesn't generate JSON Schema
class WhitespaceConstraint(BaseConstraint):
    def __get_json_schema__(self, source_type, handler):
        json_schema = handler(source_type) 
        json_schema['pattern'] = r'^(\S.*)?\S$'  # Add pattern constraint
        return json_schema
```

### 6. Update Test Infrastructure (Future)

**Current approach:** Manual testing per theme-type
**Future improvement:** Update `test.sh` to automatically:

1. Detect theme/type from example file path
2. Generate appropriate schema file
3. Validate against correct schema
4. Report results by theme-type

Example logic:

```bash
# Extract theme/type from path: reference/examples/addresses/address.yaml
theme="addresses"
type="address" 
schema_file="overture-schema-${theme}-${type}.json"

# Generate if needed, then validate
uv run python -m packages.overture-schema.src.overture.schema --theme "$theme" --type "$type" > "$schema_file"
jv "$schema_file" "$example_file"
```

## Root Cause Analysis Framework

**When counterexamples pass (should fail):**

1. ✅ **Test Pydantic model directly** - Does it catch the issue?
   - **No**: Fix the Pydantic model (add constraints)  
   - **Yes**: Continue to step 2

2. ✅ **Check JSON Schema generation** - Are constraints present?
   - **No**: Fix constraint JSON Schema generation
   - **Yes**: Continue to step 3

3. ✅ **Check validation approach** - Using per-theme-type schema?
   - **No**: Generate specific schema and test against it
   - **Yes**: Complex schema structure issue

## Success Criteria

The feedback loop is complete when:

- ✅ **Pydantic models validate correctly** (test directly with Python)
- ✅ **JSON Schema generation works** (constraints appear in schema)  
- ✅ **Per-theme-type validation works** (counterexamples fail, examples pass)
- ✅ **All theme-type combinations tested** (systematic coverage)

## Key Learnings

1. **Architecture matters:** Monolithic schema approach with conditional routing is complex and error-prone. Per-theme-type schemas are simpler and more reliable.

2. **Test Pydantic first:** Many "JSON Schema" issues are actually Pydantic model issues. Always verify models work before testing schema generation.

3. **Constraint implementation gaps:** Some constraints work in Pydantic but don't generate proper JSON Schema. Each constraint needs both validation logic AND JSON Schema generation.

4. **File organization alignment:** The per-theme-type approach naturally aligns with how examples and counterexamples are organized, making testing more intuitive.

This revised approach has proven much more effective than the original monolithic schema strategy.
