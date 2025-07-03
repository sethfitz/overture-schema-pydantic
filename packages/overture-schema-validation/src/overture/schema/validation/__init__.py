"""Constraint-based validation utilities for Overture Maps schemas.

This package provides a comprehensive set of validation constraints that can be
applied to Pydantic models to enforce data quality and business rules for
Overture Maps feature data.

Key Features:
- String pattern validation (language tags, country codes, etc.)
- Collection validation (uniqueness, size constraints)
- Numeric constraints (ranges, confidence scores)
- Conditional validation (field dependencies, mutual exclusion)
- Linear referencing validation
- Composite constraint composition

Usage:
    from overture.schema.validation import (
        LanguageTagConstraint,
        CountryCodeConstraint,
        UniqueItemsConstraint,
    )
    from typing import Annotated
    from pydantic import BaseModel, Field

    class MyModel(BaseModel):
        language: Annotated[str, LanguageTagConstraint()]
        country: Annotated[str, CountryCodeConstraint()]
        tags: Annotated[List[str], UniqueItemsConstraint()]
"""

__version__ = "0.1.0"

# Import all constraint classes for easy access
from .constraints import (
    # Base classes
    BaseConstraint,
    StringConstraint,
    CollectionConstraint,
    # String constraints
    PatternConstraint,
    LanguageTagConstraint,
    CountryCodeConstraint,
    RegionCodeConstraint,
    ISO8601DateTimeConstraint,
    JSONPointerConstraint,
    WhitespaceConstraint,
    CategoryPatternConstraint,
    WikidataConstraint,
    PhoneNumberConstraint,
    HexColorConstraint,
    NoWhitespaceConstraint,
    # Collection constraints
    UniqueItemsConstraint,
    MinItemsConstraint,
    MaxItemsConstraint,
    CompositeUniqueConstraint,
    # Numeric constraints
    ConfidenceScoreConstraint,
    ZoomLevelConstraint,
    NonNegativeConstraint,
    # Specialized constraints
    LinearReferenceRangeConstraint,
    ExtensionPrefixConstraint,
    LiteralValueConstraint,
    # Conditional constraints
    ConditionalRequiredConstraint,
    MutuallyExclusiveConstraint,
    AtLeastOneOfConstraint,
)

from .types import (
    # Commonly used constrained types
    LanguageTag,
    CountryCode,
    RegionCode,
    ISO8601DateTime,
    JSONPointer,
    LinearReferenceRange,
    ConfidenceScore,
    ZoomLevel,
    NonNegativeFloat,
    NonNegativeInt,
    CategoryPattern,
    WikidataId,
    PhoneNumber,
    HexColor,
    NoWhitespaceString,
    TrimmedString,
    # Type utilities
    theme_literal,
    type_literal,
)

__all__ = [
    # Base classes
    "BaseConstraint",
    "StringConstraint",
    "CollectionConstraint",
    # String constraints
    "PatternConstraint",
    "LanguageTagConstraint",
    "CountryCodeConstraint",
    "RegionCodeConstraint",
    "ISO8601DateTimeConstraint",
    "JSONPointerConstraint",
    "WhitespaceConstraint",
    "CategoryPatternConstraint",
    "WikidataConstraint",
    "PhoneNumberConstraint",
    "HexColorConstraint",
    "NoWhitespaceConstraint",
    # Collection constraints
    "UniqueItemsConstraint",
    "MinItemsConstraint",
    "MaxItemsConstraint",
    "CompositeUniqueConstraint",
    # Numeric constraints
    "ConfidenceScoreConstraint",
    "ZoomLevelConstraint",
    "NonNegativeConstraint",
    # Specialized constraints
    "LinearReferenceRangeConstraint",
    "ExtensionPrefixConstraint",
    "LiteralValueConstraint",
    # Conditional constraints
    "ConditionalRequiredConstraint",
    "MutuallyExclusiveConstraint",
    "AtLeastOneOfConstraint",
    # Constrained types
    "LanguageTag",
    "CountryCode",
    "RegionCode",
    "ISO8601DateTime",
    "JSONPointer",
    "LinearReferenceRange",
    "ConfidenceScore",
    "ZoomLevel",
    "NonNegativeFloat",
    "NonNegativeInt",
    "CategoryPattern",
    "WikidataId",
    "PhoneNumber",
    "HexColor",
    "NoWhitespaceString",
    "TrimmedString",
    # Type utilities
    "theme_literal",
    "type_literal",
]
