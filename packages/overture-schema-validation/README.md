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
| `PatternConstraint` | Generic regex pattern matching | Custom patterns with error messages |
| `LanguageTagConstraint` | IETF BCP-47 language tags | `"en-US"`, `"fr-CA"` |
| `CountryCodeConstraint` | ISO 3166-1 alpha-2 country codes | `"US"`, `"CA"`, `"GB"` |
| `RegionCodeConstraint` | ISO 3166-2 subdivision codes | `"US-CA"`, `"CA-ON"` |
| `ISO8601DateTimeConstraint` | ISO 8601 datetime strings | `"2023-12-25T10:30:00Z"` |
| `CategoryPatternConstraint` | Snake_case category names | `"shopping_mall"`, `"gas_station"` |
| `WikidataConstraint` | Wikidata identifiers | `"Q123456"` |
| `PhoneNumberConstraint` | International phone numbers | `"+1-555-123-4567"` |
| `HexColorConstraint` | Hexadecimal color codes | `"#FF0000"`, `"#00FF00"` |
| `JSONPointerConstraint` | RFC 6901 JSON Pointers | `"/properties/name"` |
| `WhitespaceConstraint` | No leading/trailing whitespace | Trims input validation |
| `NoWhitespaceConstraint` | No whitespace characters allowed | `"identifier123"`, `"snake_case"` |

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

### Registry Constraints

Validate against global registries and enforce schema consistency:

| Constraint | Purpose |
|------------|---------|
| `ThemeRegistryConstraint` | Validates theme field against registered themes |
| `TypeRegistryConstraint` | Validates feature type field against registered types |
| `ThemeTypeCompatibilityConstraint` | Ensures theme-type combinations are valid |
| `CountryRequiredConstraint` | Requires country field for non-country subtypes |
| `ParentDivisionConstraint` | Validates parent division logic (countries have no parent) |

**Example - Registry Validation:**

```python
from overture.schema.validation import (
    ThemeRegistryConstraint,
    TypeRegistryConstraint, 
    ThemeTypeCompatibilityConstraint
)
from overture.schema.core.base import (
    validate_theme,
    validate_feature_type,
    validate_theme_type_compatibility
)

class OvertureFeatureProperties(
    Annotated[
        BaseModel,
        ThemeRegistryConstraint(validate_theme),
        TypeRegistryConstraint(validate_feature_type),
        ThemeTypeCompatibilityConstraint(validate_theme_type_compatibility),
    ]
):
    theme: str = Field(..., description="Overture theme")
    type: str = Field(..., description="Feature type")
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

#### Replacing @model_validator

Instead of using Pydantic's `@model_validator` decorator, use constraint-based validation:

**Before (using @model_validator):**

```python
class SpeedLimitRule(BaseModel):
    max_speed: Optional[Speed] = None
    min_speed: Optional[Speed] = None
    
    @model_validator(mode="after")
    def validate_speed_required(self):
        if not self.max_speed and not self.min_speed:
            raise ValueError("Either max_speed or min_speed is required")
        return self
```

**After (using constraints):**

```python
class SpeedLimitRule(
    Annotated[BaseModel, AtLeastOneOfConstraint("max_speed", "min_speed")]
):
    max_speed: Optional[Speed] = None
    min_speed: Optional[Speed] = None
```

#### Common Migration Patterns

**Pattern 1: Range Validation**

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

**Pattern 3: Custom Pattern Validation**

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

**Pattern 4: Complex Model Validation**

```python
# Before
class DivisionBoundary(BaseModel):
    subtype: PlaceType
    country: Optional[str] = None
    is_land: Optional[bool] = None  
    is_territorial: Optional[bool] = None
    
    @model_validator(mode="after")
    def validate_country_required(self):
        if self.country is None and self.subtype != PlaceType.COUNTRY:
            raise ValueError("Country required for non-country boundaries")
        return self
        
    @model_validator(mode="after") 
    def validate_territorial_flags(self):
        if self.is_land is True and self.is_territorial is True:
            raise ValueError("is_land and is_territorial are mutually exclusive")
        return self

# After
class DivisionBoundary(
    Annotated[
        BaseModel,
        CountryRequiredConstraint(PlaceType.COUNTRY),
        MutuallyExclusiveConstraint("is_land", "is_territorial"),
    ]
):
    subtype: PlaceType
    country: Optional[str] = None
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

This validation package is designed to work seamlessly with Overture Maps schema packages and has replaced all `@model_validator` usage throughout the codebase:

```python
# In your schema models
from typing import Annotated
from overture.schema.validation import (
    CountryCode, 
    LanguageTag,
    ThemeRegistryConstraint,
    TypeRegistryConstraint,
    ParentDivisionConstraint
)

# Base properties with registry validation
class OvertureFeatureProperties(
    Annotated[
        BaseModel,
        ThemeRegistryConstraint(validate_theme),
        TypeRegistryConstraint(validate_feature_type),
    ]
):
    theme: str = Field(..., description="Overture theme")
    type: str = Field(..., description="Feature type")
    country: Optional[CountryCode] = None
    names: Dict[LanguageTag, str] = Field(default_factory=dict)

# Division-specific validation
class DivisionProperties(
    Annotated[OvertureFeatureProperties, ParentDivisionConstraint(PlaceType.COUNTRY)]
):
    subtype: PlaceType = Field(..., description="Administrative level")
    parent_division_id: Optional[str] = Field(None, description="Parent division ID")
```

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
