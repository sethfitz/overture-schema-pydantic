# Overture Schema Validation

A comprehensive constraint-based validation library for Overture Maps Pydantic
schemas. This package provides reusable validation constraints that enforce
data quality and business rules across Overture Maps feature data.

## Overview

This package provides constraint-based validation utilities for Overture Maps
Pydantic schemas, offering both field-level and model-level validation
capabilities through a comprehensive constraint system.

## Benefits of Working Constraints

- **Cleaner code**: Less boilerplate validation logic
- **Consistency**: Standardized validation patterns
- **Reusability**: Constraints can be composed and reused
- **Better errors**: Consistent, detailed validation error messages
- **JSON Schema integration**: Constraints enhance generated JSON schemas

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
| `PatternConstraint` | Generic regex pattern matching | Custom patterns |
| `LanguageTagConstraint` | IETF BCP-47 language tags | `"en-US"`, `"fr-CA"` |
| `CountryCodeConstraint` | ISO 3166-1 alpha-2 codes | `"US"`, `"CA"`, `"GB"` |
| `RegionCodeConstraint` | ISO 3166-2 subdivision codes | `"US-CA"`, `"CA-ON"` |
| `ISO8601DateTimeConstraint` | ISO 8601 datetime strings | `"2023-12-25T10Z"` |
| `CategoryPatternConstraint` | Snake_case category names | `"shopping_mall"` |
| `WikidataConstraint` | Wikidata identifiers | `"Q123456"` |
| `PhoneNumberConstraint` | International phone numbers | `"+1-555-123-4567"` |
| `HexColorConstraint` | Hexadecimal color codes | `"#FF0000"` |
| `JSONPointerConstraint` | RFC 6901 JSON Pointers | `"/properties/name"` |
| `WhitespaceConstraint` | No leading/trailing whitespace | Trims input |
| `NoWhitespaceConstraint` | No whitespace characters | `"identifier123"` |

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
| `LinearReferenceRangeConstraint` | Linear referencing ranges [start, end] |
| | where 0 ≤ start < end ≤ 1 |
| `ExtensionPrefixConstraint` | Validate extension field naming |
| `LiteralValueConstraint` | Enforce exact literal values |

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

### Registry Constraints

Registry constraints provide type-safe validation for Overture Maps themes and types:

```python
from overture.schema.validation.types import theme_literal, type_literal

class DivisionProperties(BaseModel):
    theme: theme_literal("divisions") = Field("divisions")
    type: type_literal("division") = Field("division")
```

## Ready-to-Use Types

Pre-configured type aliases for common use cases:

```python
from overture.schema.validation import (
    # String types
    LanguageTag,          # Annotated[str, LanguageTagConstraint()]
    CountryCode,          # Annotated[str, CountryCodeConstraint()]
    RegionCode,           # Annotated[str, RegionCodeConstraint()]
    ISO8601DateTime,      # Annotated[str, ISO8601DateTimeConstraint()]
    JSONPointer,          # Annotated[str, JSONPointerConstraint()]
    TrimmedString,        # Annotated[str, WhitespaceConstraint()]
    CategoryPattern,      # Annotated[str, CategoryPatternConstraint()]
    WikidataId,           # Annotated[str, WikidataConstraint()]
    PhoneNumber,          # Annotated[str, PhoneNumberConstraint()]
    HexColor,             # Annotated[str, HexColorConstraint()]
    NoWhitespaceString,   # Annotated[str, NoWhitespaceConstraint()]
    
    # Numeric types
    ConfidenceScore,      # Annotated[float, ConfidenceScoreConstraint()]
    ZoomLevel,            # Annotated[int, ZoomLevelConstraint()]
    NonNegativeFloat,     # Annotated[float, NonNegativeConstraint()]
    NonNegativeInt,       # Annotated[int, NonNegativeConstraint()]
    
    # Collection types
    LinearReferenceRange, # Annotated[List[float], LinearReferenceRangeConstraint()]
    
    # Utility functions
    theme_literal,        # Creates theme literal constraint
    type_literal,         # Creates type literal constraint
)

class MyModel(BaseModel):
    language: LanguageTag = Field(..., description="IETF BCP-47 language tag")
    country: CountryCode = Field(..., description="ISO 3166-1 alpha-2 country code")
    region: RegionCode = Field(None, description="ISO 3166-2 region code")
    confidence: ConfidenceScore = Field(..., description="ML confidence score")
    zoom: ZoomLevel = Field(..., description="Map zoom level")
    wikidata: WikidataId = Field(None, description="Wikidata identifier")
    phone: PhoneNumber = Field(None, description="International phone number")
    color: HexColor = Field("#FFFFFF", description="Hex color code")
    range: LinearReferenceRange = Field(..., description="Linear reference range")
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

Model-level validation is handled through the mixin-based constraint system and standard Pydantic validators:

```python
from pydantic import model_validator

class BoundaryProperties(BaseModel):
    is_land: Optional[bool] = None
    is_territorial: Optional[bool] = None
    
    @model_validator(mode="after")
    def validate_mutually_exclusive_flags(self):
        """Validate that is_land and is_territorial are mutually exclusive."""
        if self.is_land is True and self.is_territorial is True:
            raise ValueError(
                "is_land and is_territorial are mutually exclusive"
            )
        return self
```

### Migrating from Traditional Validators

#### Replacing @field_validator

Instead of using Pydantic's `@field_validator` decorator, use constraint annotations:

**Before (using @field_validator):**

```python
class PlaceProperties(BaseModel):
    country: str = Field(..., description="Country code")
    language: str = Field(..., description="Language tag")
    categories: List[str] = Field(..., description="Categories")
    wikidata_id: Optional[str] = Field(None, description="Wikidata ID")
    
    @field_validator("country")
    @classmethod
    def validate_country_code(cls, v):
        if not re.match(r"^[A-Z]{2}$", v):
            raise ValueError("Invalid ISO 3166-1 alpha-2 country code")
        return v
    
    @field_validator("language")
    @classmethod
    def validate_language_tag(cls, v):
        if not re.match(r"^[a-z]{2,3}(-[A-Za-z]{2,8})*$", v):
            raise ValueError("Invalid IETF BCP-47 language tag")
        return v
        
    @field_validator("categories")
    @classmethod  
    def validate_unique_categories(cls, v):
        if len(v) != len(set(v)):
            raise ValueError("Categories must be unique")
        return v
        
    @field_validator("wikidata_id")
    @classmethod
    def validate_wikidata_format(cls, v):
        if v is not None and not re.match(r"^Q\d+$", v):
            raise ValueError("Invalid Wikidata identifier format")
        return v
```

**After (using constraints):**

```python
class PlaceProperties(BaseModel):
    country: Annotated[str, CountryCodeConstraint()] = Field(
        ..., description="Country code"
    )
    language: Annotated[str, LanguageTagConstraint()] = Field(
        ..., description="Language tag"
    )
    categories: Annotated[List[str], UniqueItemsConstraint()] = Field(
        ..., description="Categories"
    )
    wikidata_id: Optional[Annotated[str, WikidataConstraint()]] = Field(
        None, description="Wikidata ID"
    )
```

#### Using Constraint-Based Validation

For complex model-level validation, use the mixin-based constraint system:

```python
from overture.schema.validation.mixin import ConstraintValidatedModel, at_least_one_of

@at_least_one_of("max_speed", "min_speed")
class SpeedLimitRule(ConstraintValidatedModel, BaseModel):
    max_speed: Optional[Speed] = None
    min_speed: Optional[Speed] = None
```

#### Common Migration Patterns

#### Pattern 1: Range Validation

```python
# Before
@field_validator("confidence")
@classmethod
def validate_confidence_range(cls, v):
    if not 0.0 <= v <= 1.0:
        raise ValueError("Confidence must be between 0.0 and 1.0")
    return v

# After  
confidence: Annotated[float, ConfidenceScoreConstraint()]
```

**Pattern 2: Multiple Field Constraints**  

```python
# Before
@field_validator("tags")
@classmethod
def validate_tags(cls, v):
    if len(v) != len(set(v)):
        raise ValueError("Tags must be unique")
    if len(v) < 1:
        raise ValueError("At least one tag required")
    return v

# After
tags: Annotated[
    List[str], 
    UniqueItemsConstraint(),
    MinItemsConstraint(1)
]
```

#### Pattern 3: Custom Pattern Validation

```python
# Before
@field_validator("postal_code") 
@classmethod
def validate_postal_code(cls, v):
    if not re.match(r"^\d{5}(-\d{4})?$", v):
        raise ValueError("Invalid ZIP code format")
    return v

# After
postal_code: Annotated[
    str, 
    PatternConstraint(r"^\d{5}(-\d{4})?$", "Invalid ZIP code format")
]
```

#### Pattern 4: Complex Model Validation

```python
# Using mixin-based constraint validation
from overture.schema.validation.mixin import ConstraintValidatedModel, mutually_exclusive

@mutually_exclusive("is_land", "is_territorial")
class DivisionBoundary(ConstraintValidatedModel, BaseModel):
    subtype: PlaceType
    is_land: Optional[bool] = None
    is_territorial: Optional[bool] = None
```

#### Migration Benefits

This constraint-based approach provides:

- **Less boilerplate**: No need to write repetitive validator methods
- **Better composition**: Multiple constraints can be easily combined
- **Reusability**: Same constraint logic can be applied to different models  
- **Type safety**: Better integration with static type checkers
- **Performance**: Constraints are compiled into Pydantic's core schema
- **Consistency**: Standardized error messages across all validations
- **JSON Schema**: Automatic enhancement of generated JSON schemas

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

This validation package integrates with Overture Maps schema packages using
a hybrid approach:

- **Field-level constraints**: Used for single-field validation
- **Mixin-based constraints**: Used for complex model-level validation
- **@model_validator**: Used for custom cross-field validation

```python
# In your schema models
from typing import Annotated
from pydantic import model_validator
from overture.schema.validation import CountryCode, LanguageTag
from overture.schema.validation.types import theme_literal, type_literal
from overture.schema.validation.mixin import ConstraintValidatedModel

# Base properties with field-level validation
class OvertureFeatureProperties(BaseModel):
    theme: str = Field(..., description="Overture theme")
    type: str = Field(..., description="Feature type")
    country: Optional[CountryCode] = None
    names: Dict[LanguageTag, str] = Field(default_factory=dict)

# Division-specific validation with mixin constraints
@required_if("subtype", "region", ["parent_division_id"])
class DivisionProperties(ConstraintValidatedModel, OvertureFeatureProperties):
    theme: theme_literal("divisions") = Field("divisions")
    type: type_literal("division") = Field("division")
    
    subtype: PlaceType = Field(..., description="Administrative level")
    parent_division_id: Optional[str] = Field(None, description="Parent ID")
```

## Alternative Approach: Mixin-Based Constraint Validation

### 🚀 NEW: Structured Constraint Validation with JSON Schema Generation

For complex model-level validation with better JSON Schema integration,
use the mixin-based approach with decorators:

#### ⚠️ CRITICAL: Inheritance Order Matters

When using `ConstraintValidatedModel`, it **MUST** come first in the inheritance list:

```python
# ✅ CORRECT - ConstraintValidatedModel first
class MyModel(ConstraintValidatedModel, BaseModel):
    pass

# ❌ WRONG - Will not generate JSON Schema metadata
class MyModel(BaseModel, ConstraintValidatedModel):
    pass
```

This is due to Python's Method Resolution Order (MRO). When `ConstraintValidatedModel`
comes first, its `model_json_schema` method is called, which adds constraint metadata
to the generated JSON Schema.

```python
from typing import Dict, List, Any, Optional, Type
from pydantic import BaseModel, model_validator, Field
from abc import ABC, abstractmethod

# Base constraint validator
class BaseConstraintValidator(ABC):
    @abstractmethod
    def validate(self, model_instance: BaseModel) -> None:
        pass
    
    @abstractmethod
    def get_json_schema_metadata(self) -> Dict[str, Any]:
        pass

# Registry for constraint validators
_constraint_registry: Dict[str, List[BaseConstraintValidator]] = {}

# Base model with constraint validation (mixin - does not inherit from BaseModel)
class ConstraintValidatedModel:
    @model_validator(mode="after")
    def validate_constraints(self):
        constraints = _constraint_registry.get(self.__class__.__name__, [])
        for constraint in constraints:
            constraint.validate(self)
        return self
    
    @classmethod
    def model_json_schema(
        cls, by_alias: bool = True, ref_template: str = "#/$defs/{model}"
    ) -> Dict[str, Any]:
        schema = super().model_json_schema(by_alias=by_alias, ref_template=ref_template)
        
        # Add constraint metadata to JSON Schema
        constraints = _constraint_registry.get(cls.__name__, [])
        if constraints:
            for constraint in constraints:
                constraint_metadata = constraint.get_json_schema_metadata()
                if constraint_metadata:
                    # Add standard JSON Schema conditionals
                    if constraint_metadata.get("if") and constraint_metadata.get("then"):
                        conditional_schema = {
                            "if": constraint_metadata["if"],
                            "then": constraint_metadata.get("then"),
                        }
                        if constraint_metadata.get("else"):
                            conditional_schema["else"] = constraint_metadata["else"]
                        
                        schema.setdefault("allOf", []).append(conditional_schema)

                    # Add custom extensions for tooling
                    schema.setdefault("x-constraints", []).append(constraint_metadata)
        
        return schema

# Decorator for mutually exclusive constraint
def mutually_exclusive(*field_names: str):
    def decorator(cls: Type[BaseModel]) -> Type[BaseModel]:
        constraint = MutuallyExclusiveValidator(field_names)
        _constraint_registry.setdefault(cls.__name__, []).append(constraint)
        return cls
    return decorator

# Usage example
@mutually_exclusive("is_land", "is_territorial")
class DivisionBoundary(ConstraintValidatedModel, BaseModel):
    is_land: Optional[bool] = Field(None, description="Land boundary flag")
    is_territorial: Optional[bool] = Field(
        None, description="Territorial boundary flag"
    )
```

### Benefits of Mixin Approach

- **Structured validation**: Clean separation of constraint logic
- **Declarative configuration**: Simple decorators for constraint application
- **JSON Schema integration**: Automatic generation of proper `if/then/else` conditionals
- **Custom extensions**: `x-constraints` metadata for tooling integration
- **Better maintainability**: Reusable constraint validators

### Generated JSON Schema

The mixin approach generates proper JSON Schema with conditional logic:

```json
{
  "type": "object",
  "properties": {
    "subtype": {"type": "string", "enum": ["country", "region", "locality"]},
    "parent_division_id": {"type": "string"}
  },
  "allOf": [
    {
      "if": {"properties": {"subtype": {"const": "country"}}},
      "then": {"not": {"required": ["parent_division_id"]}},
      "else": {"required": ["parent_division_id"]}
    }
  ],
  "x-constraints": [
    {
      "type": "mutually_exclusive_constraint",
      "fields": ["is_land", "is_territorial"]
    }
  ]
}
```

This approach provides better structure for complex validation scenarios
while maintaining full JSON Schema compatibility.

### Real-World Usage in Overture Schema

The constraint system is actively used throughout Overture Maps schema definitions:

- **Core models**: Base feature properties use registry constraints
- **Division models**: Parent-child relationship validation
- **Transportation**: Speed limit and rule validation  
- **Boundary models**: Mutual exclusion and conditional requirements
- **Extension validation**: Consistent `ext_*` prefix enforcement

## Development

The validation library is built on:

- **Pydantic v2**: Modern Python data validation
- **Type hints**: Full static type checking support  
- **Extensible design**: Easy to add new constraints
- **Test coverage**: Comprehensive validation testing

For contributing new constraints or reporting issues, see the [main repository](https://github.com/OvertureMaps/pydantic-schema).
