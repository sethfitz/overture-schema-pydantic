# Overture Schema Validation

A comprehensive constraint-based validation library for Overture Maps Pydantic schemas. This package provides reusable validation constraints that enforce data quality and business rules across Overture Maps feature data.

## Overview

Instead of writing repetitive `@field_validator` methods, you can use constraint annotations to declare validation rules declaratively. This approach provides:

- **Cleaner code**: Less boilerplate validation logic
- **Consistency**: Standardized validation patterns across all schemas
- **Reusability**: Constraints can be composed and reused
- **Better errors**: Consistent, detailed validation error messages
- **JSON Schema integration**: Constraints automatically enhance generated JSON schemas

## Installation

```bash
pip install overture-schema-validation
```

## Quick Start

```python
from typing import Annotated, List
from pydantic import BaseModel, Field
from overture.schema.validation import (
    LanguageTagConstraint,
    CountryCodeConstraint,
    UniqueItemsConstraint,
    CategoryPatternConstraint,
)

class PlaceProperties(BaseModel):
    # String pattern validation
    language: Annotated[str, LanguageTagConstraint()] = Field(
        ..., description="IETF BCP-47 language tag"
    )
    
    # Country code validation  
    country: Annotated[str, CountryCodeConstraint()] = Field(
        ..., description="ISO 3166-1 alpha-2 country code"
    )
    
    # Collection uniqueness
    categories: Annotated[
        List[str], 
        UniqueItemsConstraint(), 
        CategoryPatternConstraint()
    ] = Field(..., description="Unique place categories in snake_case")
```

## Constraint Categories

### String Pattern Constraints

Validate string formats against common patterns:

| Constraint | Purpose | Example |
|------------|---------|---------|
| `LanguageTagConstraint` | IETF BCP-47 language tags | `"en-US"`, `"fr-CA"` |
| `CountryCodeConstraint` | ISO 3166-1 alpha-2 country codes | `"US"`, `"CA"`, `"GB"` |
| `RegionCodeConstraint` | ISO 3166-2 subdivision codes | `"US-CA"`, `"CA-ON"` |
| `ISO8601DateTimeConstraint` | ISO 8601 datetime strings | `"2023-12-25T10:30:00Z"` |
| `CategoryPatternConstraint` | Snake_case category names | `"shopping_mall"`, `"gas_station"` |
| `WikidataConstraint` | Wikidata identifiers | `"Q123456"` |
| `PhoneNumberConstraint` | International phone numbers | `"+1-555-123-4567"` |
| `HexColorConstraint` | Hexadecimal color codes | `"#FF0000"`, `"#00FF00"` |
| `JSONPointerConstraint` | RFC 6901 JSON Pointers | `"/properties/name"` |

### Collection Constraints

Validate array and object collections:

| Constraint | Purpose |
|------------|---------|
| `UniqueItemsConstraint` | Ensure all items in a list are unique |
| `MinItemsConstraint` | Enforce minimum collection size |
| `MaxItemsConstraint` | Enforce maximum collection size |
| `CompositeUniqueConstraint` | Complex uniqueness based on multiple attributes |

**Example - Composite Uniqueness:**

```python
# Ensure destination labels are unique by (value, type) combination
destinations: Annotated[
    List[DestinationLabel], 
    CompositeUniqueConstraint("value", "type")
] = Field(..., description="Destination labels")
```

### Numeric Constraints

Validate numeric ranges and formats:

| Constraint | Purpose | Range |
|------------|---------|-------|
| `ConfidenceScoreConstraint` | Probability/confidence values | 0.0 - 1.0 |
| `ZoomLevelConstraint` | Map zoom levels | 0 - 23 |
| `NonNegativeConstraint` | Non-negative numbers | ≥ 0 |

### Specialized Constraints

Domain-specific validation logic:

| Constraint | Purpose |
|------------|---------|
| `LinearReferenceRangeConstraint` | Linear referencing ranges [start, end] where 0 ≤ start < end ≤ 1 |
| `ExtensionPrefixConstraint` | Validate extension field naming (e.g., `ext_*`) |
| `LiteralValueConstraint` | Enforce exact literal values (e.g., theme="places") |

### Conditional Constraints

Complex business rule validation:

| Constraint | Purpose |
|------------|---------|
| `ConditionalRequiredConstraint` | "If field A = X then field B is required" |
| `MutuallyExclusiveConstraint` | Boolean fields that cannot all be true |
| `AtLeastOneOfConstraint` | At least one of multiple fields must be present |

**Example - Conditional Logic:**

```python
from typing import Annotated
from overture.schema.validation import ConditionalRequiredConstraint

class SegmentProperties(
    Annotated[
        BaseModel,
        ConditionalRequiredConstraint("subtype", "road", ["class_"]),
        ConditionalRequiredConstraint("subtype", "rail", ["class_"]),
    ]
):
    subtype: str = Field(..., description="Segment subtype")
    class_: Optional[str] = Field(None, description="Segment class")
```

## Ready-to-Use Types

Pre-configured type aliases for common use cases:

```python
from overture.schema.validation import (
    LanguageTag,          # Annotated[str, LanguageTagConstraint()]
    CountryCode,          # Annotated[str, CountryCodeConstraint()]
    ConfidenceScore,      # Annotated[float, ConfidenceScoreConstraint()]
    CategoryPattern,      # Annotated[str, CategoryPatternConstraint()]
    # ... and many more
)

class MyModel(BaseModel):
    language: LanguageTag = Field(..., description="Language")
    country: CountryCode = Field(..., description="Country")
    confidence: ConfidenceScore = Field(..., description="Confidence")
```

## Advanced Usage

### Constraint Composition

Combine multiple constraints on a single field:

```python
tags: Annotated[
    List[str],
    UniqueItemsConstraint(),           # Must be unique
    MinItemsConstraint(1),             # At least 1 item  
    MaxItemsConstraint(10),            # At most 10 items
] = Field(..., description="Feature tags")
```

### Custom Pattern Constraints

Create domain-specific pattern validators:

```python
from overture.schema.validation import PatternConstraint

OSMIdConstraint = PatternConstraint(
    pattern=r"^[nwr]\d+$",
    error_message="Invalid OSM ID format: {value}. Must be n123, w123, or r123"
)

osm_id: Annotated[str, OSMIdConstraint] = Field(..., description="OSM ID")
```

### Model-Level Validation

Apply constraints to entire models for cross-field validation:

```python
class BoundaryProperties(
    Annotated[
        BaseModel,
        MutuallyExclusiveConstraint("is_land", "is_territorial"),
    ]
):
    is_land: Optional[bool] = None
    is_territorial: Optional[bool] = None
```

## Error Messages

Constraints provide detailed, consistent error messages:

```python
# Invalid country code
ValidationError: 1 validation error for MyModel
country
  Invalid ISO 3166-1 alpha-2 country code: USA [type=value_error]

# Mutual exclusion violation  
ValidationError: 1 validation error for BoundaryModel
is_land, is_territorial
  Fields is_land, is_territorial are mutually exclusive and cannot all be true [type=value_error]
```

## JSON Schema Generation

Constraints automatically enhance generated JSON schemas with appropriate metadata:

```python
model_schema = MyModel.model_json_schema()
# Results in enhanced JSON schema with pattern, format, and constraint information
{
  "properties": {
    "language": {
      "type": "string",
      "pattern": "^[a-z]{2,3}(-[A-Za-z]{2,8})*(-[0-9][A-Za-z0-9]{3})*$",
      "description": "IETF BCP-47 language tag"
    },
    "categories": {
      "type": "array",
      "items": {"type": "string"},
      "uniqueItems": true,
      "minItems": 1
    }
  }
}
```

## Integration with Overture Schema

This validation package is designed to work seamlessly with Overture Maps schema packages:

```python
# In your schema models
from overture.schema.validation import CountryCode, LanguageTag

class OvertureFeatureProperties(BaseModel):
    country: Optional[CountryCode] = None
    names: Dict[LanguageTag, str] = Field(default_factory=dict)
```

## Development

The validation library is built on:

- **Pydantic v2**: Modern Python data validation
- **Type hints**: Full static type checking support  
- **Extensible design**: Easy to add new constraints
- **Test coverage**: Comprehensive validation testing

For contributing new constraints or reporting issues, see the [main repository](https://github.com/OvertureMaps/pydantic-schema).
